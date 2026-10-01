import { useState } from 'react'
import { Link as RouterLink, Navigate, useNavigate } from 'react-router'
import { Alert, Box, Button, CircularProgress, Paper, TextField, Typography } from '@mui/material'

import api, { getErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function RegisterPage() {
  const { user, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>
  }
  if (user) return <Navigate to="/" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setSubmitting(true)
    try {
      await api.post('/auth/register', { email: email.trim().toLowerCase(), password })
      navigate('/login?registered=1', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 4 }, maxWidth: 440, mx: 'auto', mt: { xs: 2, sm: 6 } }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Register your login
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        Use the email on your existing customer profile. Registration can only be completed once per email.
      </Typography>

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
          autoComplete="new-password"
          slotProps={{ htmlInput: { minLength: 8, maxLength: 72 } }}
          helperText="Use 8 to 72 characters."
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Confirm password"
          type="password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          autoComplete="new-password"
          required
          fullWidth
          margin="normal"
        />
        <Button type="submit" variant="contained" size="large" fullWidth disabled={submitting} sx={{ mt: 2 }}>
          {submitting ? 'Registering…' : 'Register'}
        </Button>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
        Already registered? <RouterLink to="/login">Log in</RouterLink>
      </Typography>
    </Paper>
  )
}