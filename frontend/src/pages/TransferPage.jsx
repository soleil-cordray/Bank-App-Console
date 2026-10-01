// src/pages/TransferPage.jsx
// Send money from one of your accounts to any account number.
// POST /api/v1/transactions/transfer {from_account, to_account, amount}
// The backend checks the real rules (balance, overdraft, $10,000 limit,
// "only from your own account") and sends back a clear message if one fails.
// REFS: 07 Step 3 ("perform money transfer")

import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router'
import { Alert, Box, Button, InputAdornment, MenuItem, Paper, TextField, Typography } from '@mui/material'

import api, { getErrorMessage } from '../api/client'
import { formatMoney } from '../utils/format'

export default function TransferPage() {
  const [accounts, setAccounts] = useState([]) // fills the "From" dropdown
  const [fromAccount, setFromAccount] = useState('')
  const [toAccount, setToAccount] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null) // the Transaction the backend created
  const [submitting, setSubmitting] = useState(false)

  function loadAccounts() {
    return api.get('/accounts')
      .then((response) => setAccounts(response.data.filter((account) => account.is_active)))
      .catch((err) => setError(getErrorMessage(err)))
  }

  useEffect(() => {
    loadAccounts()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setResult(null)
    setSubmitting(true)
    try {
      const response = await api.post('/transactions/transfer', {
        from_account: fromAccount,
        to_account: toAccount.trim(),
        amount: Number(amount), // inputs give strings; the API wants a number
      })
      setResult(response.data)
      setAmount('')
      await loadAccounts() // so the dropdown shows the new balance
    } catch (err) {
      setError(getErrorMessage(err)) // e.g. "INSUFFICIENT FUNDS. ..."
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 4 }, maxWidth: 520, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Transfer money
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {result && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Sent {formatMoney(result.amount)} from #{result.from_account} to #{result.to_account}
          {' '}(transaction #{result.id}). <RouterLink to="/">Back to dashboard</RouterLink>
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        {/* select = a TextField that opens a dropdown of MenuItems */}
        <TextField
          select
          label="From account"
          value={fromAccount}
          onChange={(event) => setFromAccount(event.target.value)}
          required
          fullWidth
          margin="normal"
        >
          {accounts.map((account) => (
            <MenuItem key={account.account_number} value={account.account_number}>
              {account.type} #{account.account_number} · {formatMoney(account.balance)}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="To account number"
          value={toAccount}
          onChange={(event) => setToAccount(event.target.value)}
          helperText="The 10-digit number of the account receiving the money"
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Amount"
          type="number"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          required
          fullWidth
          margin="normal"
          slotProps={{
            input: { startAdornment: <InputAdornment position="start">$</InputAdornment> },
            // cents only, and more than zero (the backend checks this too)
            htmlInput: { min: '0.01', step: '0.01' },
          }}
        />
        <Button type="submit" variant="contained" size="large" fullWidth disabled={submitting} sx={{ mt: 2 }}>
          {submitting ? 'Sending…' : 'Send money'}
        </Button>
      </Box>
    </Paper>
  )
}
