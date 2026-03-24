/**
 * JOBPILOT — useApi Custom Hook
 *
 * Wraps API calls with loading, error, and data states.
 * Provides a consistent pattern for data fetching across all pages.
 *
 * USAGE:
 *   const { data, loading, error, refetch } = useApi(() => api.jobs.list())
 */

import { useState, useEffect, useCallback } from 'react'

export function useApi(apiCall, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiCall()
      setData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => { fetch() }, [fetch])

  return { data, setData, loading, error, refetch: fetch }
}

/**
 * useApiMutation — for POST/PATCH/DELETE operations.
 * Doesn't auto-fetch; provides an execute function.
 *
 * USAGE:
 *   const { execute, loading, error } = useApiMutation()
 *   await execute(() => api.jobs.update(id, data))
 */
export function useApiMutation() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (apiCall) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiCall()
      setLoading(false)
      return response.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      setLoading(false)
      throw err
    }
  }, [])

  return { execute, loading, error }
}
