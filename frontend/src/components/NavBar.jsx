// src/components/NavBar.jsx
// The blue bar across the top. Links only show for roles that can use them
// (role-based view rendering, REFS: 07 Step 3).

import { Link as RouterLink, useNavigate } from 'react-router'
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material'

import { useAuth } from '../auth/AuthContext'
import { CAN_TRANSFER, MANAGERS } from '../auth/roles'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <AppBar position="static" elevation={0}>
      <Toolbar sx={{ flexWrap: 'wrap', columnGap: 1 }}>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{ color: 'inherit', textDecoration: 'none', flexGrow: 1 }}
        >
          ABC Digital Bank
        </Typography>

        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
            <Button color="inherit" component={RouterLink} to="/">Dashboard</Button>
            {CAN_TRANSFER.includes(user.role) && (
              <Button color="inherit" component={RouterLink} to="/transfer">Transfer</Button>
            )}
            {MANAGERS.includes(user.role) && (
              <Button color="inherit" component={RouterLink} to="/analytics">Analytics</Button>
            )}
            {/* hidden on phones (xs) to save space */}
            <Typography variant="body2" sx={{ display: { xs: 'none', md: 'block' }, mx: 2, opacity: 0.85 }}>
              {user.email} · {user.role}
            </Typography>
            <Button color="inherit" onClick={handleLogout}>Log out</Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  )
}
