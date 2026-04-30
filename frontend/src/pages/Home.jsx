import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, AlertCircle, ChevronRight, Clock, CheckCircle, Loader2 } from 'lucide-react'
import CampaignForm from '../components/CampaignForm'
import { createCampaign, listCampaigns } from '../api'

const STATUS_STYLES = {
  generating: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30',
  ready:      'bg-green-500/10 text-green-400 border border-green-500/30',
  error:      'bg-red-500/10 text-red-400 border border-red-500/30',
}

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [campaigns, setCampaigns] = useState([])
  const [loadingCampaigns, setLoadingCampaigns] = useState(true)

  useEffect(() => {
    listCampaigns()
      .then(setCampaigns)
      .catch(() => {})
      .finally(() => setLoadingCampaigns(false))
  }, [])

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const { campaign_id } = await createCampaign(formData)
      navigate(`/campaign/${campaign_id}`)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to create campaign')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10 pt-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-violet-600 mb-4">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AI Content Calendar</h1>
          <p className="text-gray-400">
            Describe your brand and get a full multi-day social media strategy — captions, hashtags, and images.
          </p>
        </div>

        {/* Form */}
        <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800">
          <CampaignForm onSubmit={handleSubmit} loading={loading} />
          {error && (
            <div className="mt-4 flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Past campaigns */}
        {(loadingCampaigns || campaigns.length > 0) && (
          <div className="mt-10">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Previous Campaigns
            </h2>

            {loadingCampaigns ? (
              <div className="flex items-center gap-2 text-gray-600 text-sm py-4">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading…
              </div>
            ) : (
              <div className="space-y-2">
                {campaigns.map((c) => (
                  <button
                    key={c.campaign_id}
                    onClick={() => navigate(`/campaign/${c.campaign_id}`)}
                    className="w-full flex items-center justify-between bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-2xl px-5 py-4 text-left transition group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-xl bg-violet-600/20 flex items-center justify-center flex-shrink-0">
                        {c.status === 'generating'
                          ? <Clock className="w-4 h-4 text-violet-400" />
                          : <CheckCircle className="w-4 h-4 text-violet-400" />
                        }
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm text-white font-medium truncate">
                          {c.brand_prompt || c.campaign_id}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className={`inline-block text-xs px-2 py-0.5 rounded-full ${STATUS_STYLES[c.status] ?? STATUS_STYLES.ready}`}>
                            {c.status}
                          </span>
                          {c.platforms?.length > 0 && (
                            <span className="text-xs text-gray-600">
                              {c.platforms.join(', ')} · {c.num_days}d
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition flex-shrink-0" />
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
