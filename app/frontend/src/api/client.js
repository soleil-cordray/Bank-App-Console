// src/api/client.js
// ONE axios instance the whole app shares, so every request gets the token.
// REFS: 07 Step 2 ("Axios interceptor to attach JWT token")

import axios from 'axios'

// where the token is saved in the browser (see auth/AuthContext.jsx)
export const TOKEN_KEY = 'bank_token'

const api = axios.create({
  // every backend route starts with /api/v1 (app/main.py);
  // vite.config.js forwards /api to FastAPI
  baseURL: '/api/v1',
})

// REQUEST INTERCEPTOR: runs before EVERY request
// - adds "Authorization: Bearer <token>", which app/dependencies.py reads
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// RESPONSE INTERCEPTOR: runs after EVERY failed request
// - 401 = token missing / expired (JWT_EXPIRE_MINUTES, 30 by default)
//   -> forget the token and go back to the login page
// - except on /auth/login itself, where 401 just means "wrong password"
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url === '/auth/login'
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem(TOKEN_KEY)
      window.location.assign('/login?expired=1')
    }
    return Promise.reject(error)
  },
)

// ERROR MESSAGES: turn a failed request into text a person can read.
// FastAPI sends errors as {"detail": ...} (see app/main.py):
// - usually a string: "INSUFFICIENT FUNDS. This would leave ..."
// - for a badly-formed body, a LIST of problems: [{loc, msg}, ...]
export function getErrorMessage(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((problem) => problem.msg).join('; ')
  // no FastAPI answer at all: the backend is probably not running
  if (!error.response || error.response.status >= 500) {
    return "Can't reach the bank server. Is the backend running on port 8000?"
  }
  return `Something went wrong (HTTP ${error.response.status})`
}

export default api
