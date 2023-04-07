import * as path from 'path';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import mkcert from 'vite-plugin-mkcert';
import { VitePWA } from 'vite-plugin-pwa';

import manifest from './manifest.json';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      manifest,
      includeAssets: ['favicon.svg', 'favicon.ico'],
      // switch to "true" to enable sw on development
      devOptions: {
        enabled: true,
      },
    }),
    mkcert(),
  ],
  server: {
    https: true,
    proxy: {
      '/api/v1/': {
        target: 'https://m.saynschuman.pp.ua/',
        secure: false,
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
