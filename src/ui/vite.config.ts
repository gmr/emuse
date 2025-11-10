import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    strictPort: false,
    hmr: {
      clientPort: 443,
      protocol: 'wss',
    },
    cors: {
      origin: ['https://dev.emuse.org', 'http://localhost:8000'],
      credentials: true,
    },
    proxy: {
      '/api': {
        target: 'https://dev.emuse.org',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
