import { useState } from 'react'
import {
  Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, TextField, Typography,
} from '@mui/material'

import api, { getErrorMessage } from '../api/client'

export default function CreateStaffLoginDialog({ open, onClose, onCreated, branchId, branchLabel }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('TELLER')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const response = await api.post('/auth/staff', {
        email: email.trim().toLowerCase(),
        password,
        role,
        branch_id: Number(branchId),
      })
      onCreated(response.data)
      onClose()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  function handleClose() {
    if (!submitting) onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
      <Box component="form" onSubmit={handleSubmit}>
        <DialogTitle>Create staff login</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Assigned branch: {branchLabel}
          </Typography>
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
            label="Temporary password"
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
            select
            label="Role"
            value={role}
            onChange={(event) => setRole(event.target.value)}
            required
            fullWidth
            margin="normal"
          >
            <MenuItem value="TELLER">Teller</MenuItem>
            <MenuItem value="BRANCH_MANAGER">Branch manager</MenuItem>
            <MenuItem value="ADMIN">Admin</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleClose} disabled={submitting}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={submitting || !branchId}>
            {submitting ? 'Creating…' : 'Create login'}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  )
}