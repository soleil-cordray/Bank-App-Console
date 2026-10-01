// src/pages/DashboardPage.jsx
// Home page after login: account balances + recent transactions.
// - a CUSTOMER only gets their OWN accounts / transactions (the backend
//   filters by the token, see account_service.get_all_accounts)
// - staff get every account / transaction
// REFS: 07 Step 3 ("Customer Portal: view balance, account history")

import { useEffect, useState } from 'react'
import {
  Alert, Box, Card, CardContent, Chip, CircularProgress, Grid, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography,
} from '@mui/material'

import api, { getErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { formatDate, formatMoney } from '../utils/format'

const RECENT_COUNT = 10

export default function DashboardPage() {
  const { user } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // LOAD both lists once, when the page opens (the [] = "only on first render")
  useEffect(() => {
    Promise.all([api.get('/accounts'), api.get('/transactions')])
      .then(([accountsResponse, transactionsResponse]) => {
        setAccounts(accountsResponse.data)
        // the backend sends oldest first; show newest first
        const newestFirst = [...transactionsResponse.data].sort((a, b) => b.id - a.id)
        setTransactions(newestFirst.slice(0, RECENT_COUNT))
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress /></Box>
  }

  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome back
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Logged in as {user.email}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* ACCOUNTS: one card each. size = columns out of 12 at each screen width:
          phone (xs) 1 per row, tablet (sm) 2 per row, desktop (md) 3 per row */}
      <Typography variant="h6" component="h2" gutterBottom>
        Accounts
      </Typography>
      {accounts.length === 0 && !error && <Typography color="text.secondary">No accounts yet.</Typography>}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {accounts.map((account) => (
          <Grid key={account.account_number} size={{ xs: 12, sm: 6, md: 4 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="overline" color="text.secondary">{account.type}</Typography>
                  {!account.is_active && <Chip label="Closed" size="small" />}
                </Box>
                <Typography variant="h5" component="p">{formatMoney(account.balance)}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Account #{account.account_number}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* TRANSACTIONS: a plain MUI table. TableContainer scrolls sideways on phones. */}
      <Typography variant="h6" component="h2" gutterBottom>
        Recent transactions
      </Typography>
      {transactions.length === 0 && !error ? (
        <Typography color="text.secondary">No transactions yet.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>From</TableCell>
                <TableCell>To</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell sx={{ whiteSpace: 'nowrap' }}>{formatDate(transaction.created_at)}</TableCell>
                  <TableCell>{transaction.type}</TableCell>
                  {/* a DEPOSIT has no "from", a WITHDRAWAL has no "to" */}
                  <TableCell>{transaction.from_account ?? '—'}</TableCell>
                  <TableCell>{transaction.to_account ?? '—'}</TableCell>
                  <TableCell align="right">{formatMoney(transaction.amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </>
  )
}
