'use client';

import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client';
import { ApolloProvider } from '@apollo/client/react';

const graphqlUrl =
  process.env.NEXT_PUBLIC_GRAPHQL_URL ?? 'http://localhost:8000/graphql';

const client = new ApolloClient({
  link: new HttpLink({ uri: graphqlUrl }),
  cache: new InMemoryCache(),
});

export interface ApolloAppProviderProps {
  children: React.ReactNode;
}

export function ApolloAppProvider({ children }: ApolloAppProviderProps) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
