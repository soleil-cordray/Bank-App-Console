// src/theme.js
// One place to change colors, shapes, and fonts for the whole app.
// Docs: https://mui.com/material-ui/customization/theming/

import { createTheme } from '@mui/material'

const theme = createTheme({
  palette: {
    primary: { main: '#0b5cab' },
    background: { default: '#f4f6f9' },
  },
  shape: { borderRadius: 8 },
})

export default theme
