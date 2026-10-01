// src/main.jsx
// Entry point: index.html loads this file, which draws <App /> into <div id="root">.
// Each wrapper gives everything inside it one shared thing:
//   ThemeProvider -> colors / fonts     BrowserRouter -> pages + URLs
//   AuthProvider  -> who is logged in

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import { CssBaseline, ThemeProvider } from '@mui/material'

import App from './App'
import { AuthProvider } from './auth/AuthContext'
import theme from './theme'

// StrictMode (dev only) runs effects twice on purpose to catch bugs,
// so seeing every GET twice in the Network tab is normal
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
)
