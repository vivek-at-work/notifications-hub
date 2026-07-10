import type { Metadata } from 'next';

import { AppProviders } from '@/lib/providers/app-providers';

export const metadata: Metadata = {
  title: 'Notifications Hub',
  description: 'Notifications Hub admin and end-user UI',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
