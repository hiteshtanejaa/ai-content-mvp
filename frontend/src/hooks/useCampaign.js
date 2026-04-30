import { useState, useEffect, useCallback, useRef } from 'react'
import { getCampaign } from '../api'

export function useCampaign(id) {
  const [campaign, setCampaign] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)

  const refetch = useCallback(async () => {
    try {
      const data = await getCampaign(id)
      setCampaign(data)
      if (data.status !== 'generating') {
        clearInterval(intervalRef.current)
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load campaign')
      clearInterval(intervalRef.current)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    refetch()
    intervalRef.current = setInterval(refetch, 3000)
    return () => clearInterval(intervalRef.current)
  }, [refetch])

  return { campaign, loading, error, refetch }
}
