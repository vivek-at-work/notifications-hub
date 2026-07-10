import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { gql } from '@apollo/client';
import { MockedProvider, type MockedResponse } from '@apollo/client/testing';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import HomePage from '@/app/page';

const theme = createTheme();

function renderPage(mocks: ReadonlyArray<MockedResponse>) {
  return render(
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MockedProvider mocks={mocks}>
        <HomePage />
      </MockedProvider>
    </ThemeProvider>,
  );
}

const BOOTSTRAP_STATUS_QUERY = gql`
  query BootstrapStatus {
    health
    version
  }
`;

describe('HomePage', () => {
  it('renders web version and mocked API health/version', async () => {
    renderPage([
      {
        request: { query: BOOTSTRAP_STATUS_QUERY },
        result: {
          data: {
            health: 'healthy',
            version: '0.1.0',
          },
        },
      },
    ]);

    expect(screen.getByText(/Web: web@0\.1\.0/)).toBeInTheDocument();
    expect(await screen.findByText(/API health: healthy/)).toBeInTheDocument();
    expect(screen.getByText(/API version: 0\.1\.0/)).toBeInTheDocument();
  });

  it('shows API unreachable message when query fails', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);

    renderPage([
      {
        request: { query: BOOTSTRAP_STATUS_QUERY },
        error: new Error('Network error'),
      },
    ]);

    expect(await screen.findByText(/API unreachable/)).toBeInTheDocument();
    consoleSpy.mockRestore();
  });
});
