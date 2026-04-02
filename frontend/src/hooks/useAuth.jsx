/**
 * Auth context — stores token + user, provides login/register/logout.
 *
 * Token lifecycle:
 *  - Stored in localStorage so it survives page refreshes
 *  - Attached to every request via the Axios interceptor in api/client.js
 *  - Cleared on logout or when the server returns 401/403 (interceptor handles that)
 *
 * The `loading` state is true during the initial mount check. Protected routes
 * should render nothing (or a spinner) while loading=true to avoid a flash of
 * unauthenticated content before the token is verified.
 */
import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)  // true until initial token check completes

  useEffect(() => {
    // On mount: if a token exists in localStorage, verify it with the backend.
    // This handles the case where the user refreshes the page — we need to
    // re-hydrate the user object from a valid token, not just trust localStorage blindly.
    const token = localStorage.getItem('token')
    if (!token) { setLoading(false); return }
    api.auth.me()
      .then(res => setUser(res.data))
      .catch(() => localStorage.removeItem('token'))  // expired/invalid token → clear it
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await api.auth.login({ email, password })
    localStorage.setItem('token', data.token)
    setUser(data.user)
  }

  const register = async (email, password, full_name) => {
    const { data } = await api.auth.register({ email, password, full_name })
    localStorage.setItem('token', data.token)
    setUser(data.user)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
