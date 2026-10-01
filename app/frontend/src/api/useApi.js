// src/api/useApi.js
// A custom hook: GET a URL and keep the answer in state.
//   const accounts = useApi('/accounts')
//   accounts.data / accounts.error / accounts.loading
// It re-fetches whenever the URL changes (e.g. a new ?month=).
// Pass null to skip the request (e.g. while an input is empty).

import { useEffect, useState } from 'react'

import api, { getErrorMessage } from './client'

export default function useApi(url) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!url) return
    // if the URL changes before this answer arrives, ignore the old answer
    // (otherwise a slow old request could overwrite a newer one)
    let ignore = false
    setLoading(true)
    setError('')
    api.get(url)
      .then((response) => { if (!ignore) setData(response.data) })
      .catch((err) => { if (!ignore) setError(getErrorMessage(err)) })
      .finally(() => { if (!ignore) setLoading(false) })
    return () => { ignore = true }
  }, [url])

  if (!url) return { data: null, error: '', loading: false }
  return { data, error, loading }
}
