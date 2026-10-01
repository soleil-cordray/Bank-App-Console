import { useState } from 'react'
import { Alert, Box, Button, MenuItem, TextField, Typography } from '@mui/material'

import api, { getErrorMessage } from '../api/client'

export default function AccountCreationForm({ ownerId, branchId, onCreated, submitLabel = 'Create account' }) {
  const [accountType, setAccountType] = useState('CHECKING')
  const [balance, setBalance] = useState('0')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const response = await api.post('/accounts', {
        owner_id: Number(ownerId),
        type: accountType,
        branch_id: Number(branchId),
        balance: Number(balance),
      })
      onCreated(response.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="subtitle1" component="h2" sx={{ mt: 2 }}>
        Account details
      </Typography>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      <TextField
        select
        label="Account type"
        value={accountType}
        onChange={(event) => setAccountType(event.target.value)}
        required
        fullWidth
        margin="normal"
      >
        <MenuItem value="CHECKING">Checking</MenuItem>
        <MenuItem value="SAVINGS">Savings</MenuItem>
      </TextField>
      <TextField
        label="Opening balance"
        type="number"
        value={balance}
        onChange={(event) => setBalance(event.target.value)}
        helperText={accountType === 'SAVINGS' ? 'Minimum opening balance: $100.00' : 'Optional for checking accounts'}
        required
        fullWidth
        margin="normal"
        slotProps={{
          htmlInput: { min: accountType === 'SAVINGS' ? '100' : '0', step: '0.01' },
        }}
      />
      <Button type="submit" variant="contained" size="large" fullWidth disabled={submitting} sx={{ mt: 2 }}>
        {submitting ? 'Opening account…' : submitLabel}
      </Button>
    </Box>
  )
}