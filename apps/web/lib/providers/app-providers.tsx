'use client';

import { ApolloAppProvider } from './apollo-provider';
import { MuiProvider } from './mui-provider';
import { ReduxProvider } from './redux-provider';

export interface AppProvidersProps {
  children: React.ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <ReduxProvider>
      <ApolloAppProvider>
        <MuiProvider>{children}</MuiProvider>
      </ApolloAppProvider>
    </ReduxProvider>
  );
}
