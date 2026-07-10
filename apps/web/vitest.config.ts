import path from 'node:path';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
      '@notifications-hub/design-system': path.resolve(
        __dirname,
        '../../libs/js/design-system/src/index.ts',
      ),
      '@notifications-hub/notifications-ui': path.resolve(
        __dirname,
        '../../libs/js/notifications-ui/src/index.ts',
      ),
    },
  },
});
