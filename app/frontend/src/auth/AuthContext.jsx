// src/auth/AuthContext.jsx
// Remembers WHO is logged in, and shares it with every component.
//   const { user, login, logout } = useAuth()
// REFS: 07 Step 2 ("Auth Context to persist JWT in memory/local storage")

import { createContext, useContext, useEffect, useState } from 'react'

import api, { TOKEN_KEY } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // user = what GET /auth/me returns: {login_id, email, role, customer_id, branch_id}
  const [user, setUser] = useState(null)
  // true until we know whether a token saved last time still works
  const [loading, setLoading] = useState(true)

  // ON PAGE LOAD: is there a saved token? Ask the backend who it belongs to.
  // (a refresh wipes React state, but localStorage survives it)
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) {
      setLoading(false)
      return
    }
    api.get('/auth/me')
      .then((response) => setUser(response.data))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    // the backend expects a FORM with "username" + "password", not JSON
    // (the OAuth2 standard; see app/controllers/auth_controller.py)
    const form = new URLSearchParams({ username: email, password })
    const response = await api.post('/auth/login', form)
    localStorage.setItem(TOKEN_KEY, response.data.access_token)

    const me = await api.get('/auth/me')
    setUser(me.data)
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }

  // React 19: a context is its own provider (no ".Provider" needed)
  return (
    <AuthContext value={{ user, loading, login, logout }}>
      {children}
    </AuthContext>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
