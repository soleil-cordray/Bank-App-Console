// src/pages/AnalyticsPage.jsx
// Manager Dashboard: only BRANCH_MANAGER and ADMIN can open it (see App.jsx).
// - ADMIN picks any branch; a BRANCH_MANAGER always sees their own
//   (the backend refuses other branches with 403 anyway)
// Endpoints used (app/controllers/branch_controller.py):
//   GET /branches, GET /branches/{id}                       branch + staff_list
//   GET /branches/analytics/transaction-volume              one branch, one month
//   GET /branches/analytics/monthly-transfer-volume         every branch, every month
//   GET /branches/analytics/staff-to-manager-ratio?limit=   branches over the limit
//   GET /branches/analytics/non-direct-staff-ratio?threshold=
// REFS: 07 Step 3 ("Manager Dashboard: branch staff distribution and
//       performance indicators"), 1.3 + 3.3 (the analytics questions)

import { useState } from 'react'
import {
  Alert, Grid, MenuItem, Paper, TextField, Typography,
} from '@mui/material'

import useApi from '../api/useApi'
import { useAuth } from '../auth/AuthContext'
import { AnalyticsSection, AnalyticsStatCard, BranchStaffSection } from '../components/AnalyticsComponents'
import CreateStaffLoginDialog from '../components/CreateStaffLoginDialog'
import DataTable from '../components/DataTable'
import { formatMoney } from '../utils/format'

// "2026-10" for the current month (what <input type="month"> uses)
function thisMonth() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

function percent(ratio) {
  return `${Math.round(ratio * 100)}%`
}

export default function AnalyticsPage() {
  const { user } = useAuth()
  const isAdmin = user.role === 'ADMIN'
  const canViewStaff = isAdmin || user.role === 'BRANCH_MANAGER'

  // WHICH BRANCH: an ADMIN picks from the list (first branch until they choose)
  const branches = useApi(isAdmin ? '/branches' : null)
  const [pickedBranchId, setPickedBranchId] = useState('')
  const branchId = isAdmin ? (pickedBranchId || branches.data?.[0]?.branch_id) : user.branch_id
  const [createStaffOpen, setCreateStaffOpen] = useState(false)
  const [createdStaff, setCreatedStaff] = useState(null)

  // WHICH MONTH + the two "flag branches over ..." limits
  const [month, setMonth] = useState(thisMonth())
  const [maxStaffPerManager, setMaxStaffPerManager] = useState('1')
  const [maxContractPercent, setMaxContractPercent] = useState('20')
  // check the inputs here, so the message is in the units the person typed
  // (the backend wants the contract limit as 0-1, the page asks for 0-100%)
  const staffLimitOk = maxStaffPerManager !== '' && Number(maxStaffPerManager) >= 0
  const contractLimitOk = maxContractPercent !== ''
    && Number(maxContractPercent) >= 0 && Number(maxContractPercent) <= 100

  // DATA: each one re-fetches by itself when its URL changes
  // (null = skip, e.g. while an input is invalid)
  const branch = useApi(branchId ? `/branches/${branchId}` : null)
  const branchStaff = useApi(canViewStaff && branchId ? `/branches/${branchId}/staff` : null)
  const volume = useApi(branchId && month
    ? `/branches/analytics/transaction-volume?branch_id=${branchId}&month=${month}` : null)
  const monthlyTransfers = useApi('/branches/analytics/monthly-transfer-volume')
  const overManaged = useApi(staffLimitOk
    ? `/branches/analytics/staff-to-manager-ratio?limit=${maxStaffPerManager}` : null)
  const contractHeavy = useApi(contractLimitOk
    ? `/branches/analytics/non-direct-staff-ratio?threshold=${Number(maxContractPercent) / 100}` : null)

  if (isAdmin && branches.data?.length === 0) {
    return <Alert severity="info">No branches yet. Create one with POST /branches first.</Alert>
  }

  const staff = branchStaff.data ?? []
  return (
    <>
      <Typography variant="h4" component="h1" gutterBottom>
        Branch analytics
      </Typography>

      {createdStaff && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Created {createdStaff.role.toLowerCase().replace('_', ' ')} login for {createdStaff.email}
          {' '}in branch #{createdStaff.branch_id}.
        </Alert>
      )}

      {/* CONTROLS: which branch + which month */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        {isAdmin ? (
          <TextField
            select
            label="Branch"
            value={branchId ?? ''}
            onChange={(event) => {
              setPickedBranchId(event.target.value)
              setCreatedStaff(null)
            }}
            sx={{ minWidth: 240 }}
          >
            {(branches.data ?? []).map((option) => (
              <MenuItem key={option.branch_id} value={option.branch_id}>
                {option.branch_code} · {option.location}
              </MenuItem>
            ))}
          </TextField>
        ) : (
          <Typography sx={{ minWidth: 240 }}>
            <strong>Your branch:</strong> {branch.data ? `${branch.data.branch_code} · ${branch.data.location}` : '…'}
          </Typography>
        )}
        <TextField
          label="Month"
          type="month"
          value={month}
          onChange={(event) => setMonth(event.target.value)}
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Paper>
      {isAdmin && createStaffOpen && (
        <CreateStaffLoginDialog
          open={createStaffOpen}
          onClose={() => setCreateStaffOpen(false)}
          onCreated={setCreatedStaff}
          branchId={branchId}
          branchLabel={branch.data
            ? `${branch.data.branch_code} · ${branch.data.location} (#${branchId})`
            : `Branch #${branchId}`}
        />
      )}

      {/* PERFORMANCE INDICATORS for the chosen branch + month */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: isAdmin ? 4 : 6 }}>
          <AnalyticsStatCard
            label="Transaction volume"
            value={volume.data ? formatMoney(volume.data.total_volume) : null}
            note="deposits + withdrawals + transfers"
            loading={volume.loading}
            error={volume.error}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: isAdmin ? 4 : 6 }}>
          <AnalyticsStatCard
            label="Transactions"
            value={volume.data?.transaction_count}
            note={`in ${month || 'the chosen month'}`}
            loading={volume.loading}
            error={volume.error}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: isAdmin ? 4 : 6 }}>
          <AnalyticsStatCard
            label="Staff"
            value={branchStaff.data ? staff.length : null}
            note="active logins assigned to this branch"
            loading={branchStaff.loading}
            error={branchStaff.error}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        {/* STAFF DISTRIBUTION for the chosen branch */}
        {canViewStaff && (
          <Grid size={{ xs: 12, md: 6 }}>
            <BranchStaffSection
              staff={staff}
              loading={branchStaff.loading}
              error={branchStaff.error}
              canCreateStaff={isAdmin && Boolean(branchId)}
              onCreateStaff={() => setCreateStaffOpen(true)}
            />
          </Grid>
        )}

        {/* TRANSFERS per branch per month (every branch) */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AnalyticsSection title="Monthly transfer volume" loading={monthlyTransfers.loading} error={monthlyTransfers.error}>
            <DataTable
              rows={monthlyTransfers.data ?? []}
              rowKey={(row) => `${row.branch_id}-${row.month}`}
              emptyText="No transfers yet."
              columns={[
                { label: 'Branch', render: (row) => `#${row.branch_id}` },
                { label: 'Month', render: (row) => row.month },
                { label: 'Transfers', render: (row) => row.transfer_count, align: 'right' },
                { label: 'Total', render: (row) => formatMoney(row.total_transferred), align: 'right' },
              ]}
            />
          </AnalyticsSection>
        </Grid>

        {/* FLAGGED: too many staff per manager (every branch) */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AnalyticsSection
            title="Staff per manager over limit"
            loading={overManaged.loading}
            error={staffLimitOk ? overManaged.error : 'Enter a limit of 0 or more.'}
            control={
              <TextField
                label="Limit"
                type="number"
                size="small"
                error={!staffLimitOk}
                value={maxStaffPerManager}
                onChange={(event) => setMaxStaffPerManager(event.target.value)}
                slotProps={{ htmlInput: { min: 0, step: 0.5 } }}
                sx={{ width: 100 }}
              />
            }
          >
            <DataTable
              rows={overManaged.data ?? []}
              rowKey={(row) => row.branch_id}
              emptyText="No branch is over this limit."
              columns={[
                { label: 'Branch', render: (row) => row.branch_code },
                // null = the branch has staff but no manager at all
                { label: 'Staff per manager', render: (row) => row.staff_to_manager_ratio ?? 'No manager', align: 'right' },
              ]}
            />
          </AnalyticsSection>
        </Grid>

        {/* FLAGGED: too many contract staff (every branch) */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AnalyticsSection
            title="Contract staff over limit"
            loading={contractHeavy.loading}
            error={contractLimitOk ? contractHeavy.error : 'Enter a percent from 0 to 100.'}
            control={
              <TextField
                label="Limit %"
                type="number"
                size="small"
                error={!contractLimitOk}
                value={maxContractPercent}
                onChange={(event) => setMaxContractPercent(event.target.value)}
                slotProps={{ htmlInput: { min: 0, max: 100, step: 5 } }}
                sx={{ width: 100 }}
              />
            }
          >
            <DataTable
              rows={contractHeavy.data ?? []}
              rowKey={(row) => row.branch_id}
              emptyText="No branch is over this limit."
              columns={[
                { label: 'Branch', render: (row) => row.branch_code },
                { label: 'Contract / total', render: (row) => `${row.non_direct_staff} / ${row.total_staff}`, align: 'right' },
                { label: 'Share', render: (row) => percent(row.non_direct_ratio), align: 'right' },
              ]}
            />
          </AnalyticsSection>
        </Grid>
      </Grid>
    </>
  )
}

