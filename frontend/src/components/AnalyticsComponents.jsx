import { Alert, Box, Button, Card, CardContent, Chip, CircularProgress, Paper, Typography } from '@mui/material'

import DataTable from './DataTable'

export function AnalyticsStatCard({ label, value, note, loading, error }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="overline" color="text.secondary">{label}</Typography>
        {error ? (
          <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>
        ) : (
          <>
            <Typography variant="h4" component="p">
              {loading ? <CircularProgress size={28} /> : (value ?? '—')}
            </Typography>
            <Typography variant="body2" color="text.secondary">{note}</Typography>
          </>
        )}
      </CardContent>
    </Card>
  )
}

export function AnalyticsSection({ title, control, footer, loading, error, children }) {
  return (
    <Paper
      component="section"
      sx={{ p: 2, height: '100%' }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 2, mb: 1 }}>
        <Typography variant="h6" component="h2">{title}</Typography>
        {control}
      </Box>
      {error && <Alert severity="error">{error}</Alert>}
      {!error && loading && <CircularProgress size={24} />}
      {!error && !loading && children}
      {footer && (
        <Box
          component="footer"
          sx={{
            display: 'flex',
            justifyContent: 'flex-start',
            mt: 2,
            pt: 2,
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          {footer}
        </Box>
      )}
    </Paper>
  )
}

export function BranchStaffSection({ staff, loading, error, canCreateStaff, onCreateStaff }) {
  return (
    <AnalyticsSection
      title="Staff logins"
      loading={loading}
      error={error}
      footer={canCreateStaff && (
        <Button variant="contained" onClick={onCreateStaff}>
          Create staff login
        </Button>
      )}
    >
      <DataTable
        rows={staff}
        rowKey={(member) => member.login_id}
        emptyText="No staff logins assigned to this branch."
        columns={[
          { label: 'Email', render: (member) => member.email },
          {
            label: 'Type',
            render: (member) => <Chip
              label={member.role.replace('_', ' ')}
              size="small"
              color={member.role === 'BRANCH_MANAGER' ? 'primary' : 'default'}
            />,
          },
        ]}
      />
    </AnalyticsSection>
  )
}