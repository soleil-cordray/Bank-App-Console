// src/components/ProtectedRoute.jsx
// Wrap a page in this to require a login (and, optionally, certain roles):
//   <ProtectedRoute>                      any logged-in user
//   <ProtectedRoute roles={MANAGERS}>     only these roles
// The frontend version of require_roles(...) in app/dependencies.py.
// It only HIDES pages; the backend still refuses the data (401 / 403).

import { Navigate } from 'react-router'
import { Box, CircularProgress } from '@mui/material'

import { useAuth } from '../auth/AuthContext'

export default function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth()

  // still checking a saved token: show a spinner, not the login page
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}
