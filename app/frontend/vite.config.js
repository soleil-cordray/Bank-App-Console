// frontend/vite.config.js
// Settings for the dev server (npm run dev) and the build (npm run build).

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // PROXY: the browser only ever talks to THIS server (port 5173);
    // anything starting with /api is forwarded to FastAPI (port 8000).
    // - same origin for the browser = no CORS setup needed on the backend
    // - 127.0.0.1, not localhost: on Windows "localhost" can resolve to
    //   IPv6 (::1), but uvicorn only listens on IPv4 by default
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
