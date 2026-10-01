import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router'
import { Alert, Box, Button, MenuItem, Paper, TextField, Typography } from '@mui/material'

import api, { getErrorMessage } from '../api/client'
import AccountCreationForm from '../components/AccountCreationForm'

export default function NewCustomerPage() {
  const [branches, setBranches] = useState([])
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [branchId, setBranchId] = useState('')
  const [customer, setCustomer] = useState(null)
  const [createdAccount, setCreatedAccount] = useState(null)
  const [error, setError] = useState('')
  const [loadingBranches, setLoadingBranches] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get('/branches')
      .then((response) => setBranches(response.data.filter((branch) => branch.is_active)))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoadingBranches(false))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const response = await api.post('/customers', {
        name: name.trim(),
        email: email.trim(),
        branch_id: Number(branchId),
      })
      setCustomer(response.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Paper sx={{ p: { xs: 2, sm: 4 }, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Create a customer
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {customer && !createdAccount && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Customer profile for {customer.name} created. Open their first account below.
        </Alert>
      )}
      {createdAccount && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Customer {customer.name} and {createdAccount.type.toLowerCase()} account
          {' '}#{createdAccount.account_number} created. <RouterLink to="/">Go to dashboard</RouterLink>
        </Alert>
      )}

      {!customer && <Box component="form" onSubmit={handleSubmit}>
        <Typography variant="subtitle1" component="h2" sx={{ mt: 1 }}>
          Customer details
        </Typography>
        <TextField
          label="Full name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          fullWidth
          margin="normal"
          disabled={Boolean(customer)}
        />
        <TextField
          label="Email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
          fullWidth
          margin="normal"
          disabled={Boolean(customer)}
        />
        <TextField
          select
          label="Branch"
          value={branchId}
          onChange={(event) => setBranchId(event.target.value)}
          required
          fullWidth
          margin="normal"
          disabled={Boolean(customer) || loadingBranches || branches.length === 0}
        >
          {branches.map((branch) => (
            <MenuItem key={branch.branch_id} value={branch.branch_id}>
              {branch.branch_code} · {branch.location}
            </MenuItem>
          ))}
        </TextField>
        {branches.length === 0 && !loadingBranches && !error && (
          <Alert severity="info" sx={{ mt: 2 }}>Create an active branch before opening an account.</Alert>
        )}
        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          disabled={submitting || loadingBranches || branches.length === 0}
          sx={{ mt: 2 }}
        >
          {submitting ? 'Creating customer…' : 'Create customer'}
        </Button>
      </Box>}
      {customer && !createdAccount && (
        <AccountCreationForm
          ownerId={customer.customer_id}
          branchId={customer.branch_id}
          submitLabel="Open first account"
          onCreated={setCreatedAccount}
        />
      )}
      {createdAccount && (
        <Button variant="outlined" onClick={() => {
          setCustomer(null)
          setCreatedAccount(null)
          setName('')
          setEmail('')
          setBranchId('')
        }} sx={{ mt: 2 }}>
          Create another customer
        </Button>
      )}
    </Paper>
  )
}