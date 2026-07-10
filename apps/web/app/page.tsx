'use client';

import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { gql } from '@apollo/client';
import { useQuery } from '@apollo/client/react';
import { NotificationBadge } from '@notifications-hub/notifications-ui';

import { appName, appVersion } from '@/lib/version';

const BOOTSTRAP_STATUS_QUERY = gql`
  query BootstrapStatus {
    health
    version
  }
`;

interface BootstrapStatusData {
  health: string;
  version: string;
}

export default function HomePage() {
  const { data, loading, error } = useQuery<BootstrapStatusData>(BOOTSTRAP_STATUS_QUERY);

  return (
    <Box component="main" sx={{ p: 4, maxWidth: 640 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Notifications Hub
      </Typography>

      <Stack spacing={2}>
        <Typography variant="body1">
          Web: {appName}@{appVersion}
        </Typography>

        {loading && (
          <Stack direction="row" spacing={1} alignItems="center">
            <CircularProgress size={20} />
            <Typography variant="body2">Loading API status…</Typography>
          </Stack>
        )}

        {error && (
          <Alert severity="warning">
            API unreachable: {error.message}. Start the API with{' '}
            <code>make api-dev</code>.
          </Alert>
        )}

        {data && (
          <>
            <Typography variant="body1">API health: {data.health}</Typography>
            <Typography variant="body1">API version: {data.version}</Typography>
          </>
        )}

        <Box sx={{ pt: 2 }}>
          <NotificationBadge count={3} />
        </Box>
      </Stack>
    </Box>
  );
}
