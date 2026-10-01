import { useEffect, useState } from 'react'
import { Alert, MenuItem, Paper, TextField, Typography } from '@mui/material'

import AccountCreationForm from '../components/AccountCreationForm'
import api, { getErrorMessage } from '../api/client'

export default function NewAccountPage() {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [createdAccount, setCreatedAccount] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/customers')
      .then((response) => setCustomers(response.data.filter((customer) => customer.is_active)))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  const selectedCustomer = customers.find((customer) => customer.customer_id === Number(customerId))

  return (
    <Paper sx={{ p: { xs: 2, sm: 4 }, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Open a new account
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {createdAccount && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {createdAccount.type.toLowerCase()} account #{createdAccount.account_number} opened for customer
          {' '}#{createdAccount.owner_id}.
        </Alert>
      )}
      {!loading && !error && customers.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>Create a customer profile before opening an account.</Alert>
      )}
      <TextField
        select
        label="Customer"
        value={customerId}
        onChange={(event) => {
          setCustomerId(event.target.value)
          setCreatedAccount(null)
        }}
        required
        fullWidth
        margin="normal"
        disabled={loading || customers.length === 0}
      >
        {customers.map((customer) => (
          <MenuItem key={customer.customer_id} value={customer.customer_id}>
            {customer.name} · {customer.email} · #{customer.customer_id}
          </MenuItem>
        ))}
      </TextField>
      {selectedCustomer && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Branch #{selectedCustomer.branch_id}
          </Typography>
          <AccountCreationForm
            key={selectedCustomer.customer_id}
            ownerId={selectedCustomer.customer_id}
            branchId={selectedCustomer.branch_id}
            onCreated={setCreatedAccount}
          />
        </>
      )}
    </Paper>
  )
}