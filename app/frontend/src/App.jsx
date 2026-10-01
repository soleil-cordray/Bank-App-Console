// src/App.jsx
// The page list: which URL shows which page, and who may open it.
// REFS: 07 Step 1 ("Navigation Bar, Dashboard, Analytics View, Account View")

import { Navigate, Route, Routes } from 'react-router'
import { Container } from '@mui/material'

import { CAN_TRANSFER, MANAGERS } from './auth/roles'
import NavBar from './components/NavBar'
import ProtectedRoute from './components/ProtectedRoute'
import AnalyticsPage from './pages/AnalyticsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import TransferPage from './pages/TransferPage'

export default function App() {
  return (
    <>
      <NavBar />
      <Container component="main" maxWidth="lg" sx={{ py: 4 }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="/" element={
            <ProtectedRoute><DashboardPage /></ProtectedRoute>
          } />
          <Route path="/transfer" element={
            <ProtectedRoute roles={CAN_TRANSFER}><TransferPage /></ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute roles={MANAGERS}><AnalyticsPage /></ProtectedRoute>
          } />

          {/* any other URL -> dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </>
  )
}
