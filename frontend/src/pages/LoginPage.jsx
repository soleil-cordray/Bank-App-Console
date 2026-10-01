// src/pages/LoginPage.jsx
// Email + password form. On success, AuthContext saves the token.
// REFS: 07 Step 2

import { useState } from 'react'
import { Link as RouterLink, Navigate, useNavigate, useSearchParams } from 'react-router'
import { Alert, Box, Button, Paper, TextField, Typography } from '@mui/material'

import { getErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  // FORM STATE: one useState per input ("controlled inputs")
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // already logged in? skip the form
  if (user) return <Navigate to="/" replace />

  async function handleSubmit(event) {
    event.preventDefault() // stop the browser's own full-page form submit
    setError('')
    setSubmitting(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(getErrorMessage(err)) // e.g. "Invalid email or password"
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Paper sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: { xs: 2, sm: 6 } }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Log in
      </Typography>

      {/* client.js sends people here with ?expired=1 after a 401 */}
      {searchParams.get('expired') && !error && (
        <Alert severity="info" sx={{ mb: 2 }}>Your session expired. Please log in again.</Alert>
      )}
      {searchParams.get('registered') && !error && (
        <Alert severity="success" sx={{ mb: 2 }}>Registration complete. You can now log in.</Alert>
      )}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          autoFocus
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          required
          fullWidth
          margin="normal"
        />
        <Button type="submit" variant="contained" size="large" fullWidth disabled={submitting} sx={{ mt: 2 }}>
          {submitting ? 'Logging in…' : 'Log in'}
        </Button>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
        Need a login? <RouterLink to="/register">Register</RouterLink>
      </Typography>
    </Paper>
  )
}
