// src/components/DataTable.jsx
// A small reusable table: describe the columns once, pass the rows.
//   <DataTable
//     rows={branches}
//     rowKey={(branch) => branch.branch_id}
//     columns={[
//       { label: 'Branch', render: (branch) => branch.branch_code },
//       { label: 'Total', render: (branch) => formatMoney(branch.total), align: 'right' },
//     ]}
//   />

import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material'

export default function DataTable({ columns, rows, rowKey, emptyText = 'Nothing to show.' }) {
  if (rows.length === 0) {
    return <Typography color="text.secondary" sx={{ py: 1 }}>{emptyText}</Typography>
  }
  return (
    // TableContainer scrolls sideways on narrow screens instead of squashing
    <TableContainer>
      <Table size="small">
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.label} align={column.align}>{column.label}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={rowKey(row)}>
              {columns.map((column) => (
                <TableCell key={column.label} align={column.align}>{column.render(row)}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
