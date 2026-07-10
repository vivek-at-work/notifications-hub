import type { NextConfig } from 'next';

import packageJson from './package.json';

const nextConfig: NextConfig = {
  transpilePackages: ['@notifications-hub/design-system', '@notifications-hub/notifications-ui'],
  env: {
    NEXT_PUBLIC_APP_VERSION: packageJson.version,
    NEXT_PUBLIC_APP_NAME: packageJson.name,
  },
};

export default nextConfig;
