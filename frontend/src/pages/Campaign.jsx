import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CalendarDays, CheckCircle, Clock, Loader2, AlertCircle, Sparkles } from 'lucide-react'
import { useCampaign } from '../hooks/useCampaign'
import { scheduleAll } from '../api'
import PostCard from '../components/PostCard'
import AgentDashboard from '../components/AgentDashboard'

export default function Campaign() {
  const { campaignId } = useParams()
  const navigate = useNavigate()
  const { campaign, loading, error, refetch } = useCampaign(campaignId)
  const [scheduling, setScheduling] = useState(false)
  const [scheduleMsg, setScheduleMsg] = useState(null)

  const handleScheduleAll = async () => {
    setScheduling(true)
    setScheduleMsg(null)
    try {
      const { scheduled } = await scheduleAll(campaignId)
      setScheduleMsg(`${scheduled} post${scheduled !== 1 ? 's' : ''} scheduled!`)
      await refetch()
    } catch (err) {
      setScheduleMsg(err?.response?.data?.detail || 'Scheduling failed')
    } finally {
      setScheduling(false)
    }
  }

  // ── Loading state ────────────────────────────────────────────────────────
  if (loading && !campaign) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-400" />
      </div>
    )
  }

  // ── Error state ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-white text-lg font-semibold mb-2">Something went wrong</p>
          <p className="text-gray-400 mb-6">{error}</p>
          <button onClick={() => navigate('/')} className="bg-violet-600 hover:bg-violet-500 text-white px-6 py-2.5 rounded-xl transition font-medium">
            ← Back
          </button>
        </div>
      </div>
    )
  }

  // ── Campaign error state ─────────────────────────────────────────────────
  if (campaign?.status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-white text-lg font-semibold mb-2">Generation failed</p>
          <p className="text-gray-400 text-sm mb-2">
            {campaign?.errors?.[0] ?? 'Unknown error'}
          </p>
          <button onClick={() => navigate('/')} className="mt-4 bg-violet-600 hover:bg-violet-500 text-white px-6 py-2.5 rounded-xl transition font-medium">
            ← Try again
          </button>
        </div>
      </div>
    )
  }

  // ── Generating state ─────────────────────────────────────────────────────
  if (campaign?.status === 'generating') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center max-w-md">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-600/20 mb-5">
            <Sparkles className="w-8 h-8 text-violet-400 animate-pulse" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Generating your content calendar…</h2>
          <p className="text-gray-400 text-sm mb-4">
            GPT-4o is writing captions and DALL-E 3 is generating images.
            This usually takes <span className="text-violet-300 font-medium">60–90 seconds</span>.
          </p>
          <div className="flex items-center justify-center gap-2 text-gray-500 text-xs">
            <Loader2 className="w-4 h-4 animate-spin" /> Checking for updates…
          </div>
        </div>
      </div>
    )
  }

  // ── Ready state ──────────────────────────────────────────────────────────
  const posts = campaign?.posts ?? []
  const approvedCount  = posts.filter((p) => p?.status === 'approved').length
  const scheduledCount = posts.filter((p) => p?.status === 'scheduled').length
  const totalCount     = posts.length
  const platformList   = campaign?.platforms ?? []
  const hasApproved    = approvedCount > 0

  const brandSnippet = (campaign?.brand_prompt ?? '').slice(0, 120) +
    ((campaign?.brand_prompt?.length ?? 0) > 120 ? '…' : '')

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-gray-950/90 backdrop-blur border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 transition flex-shrink-0"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="min-w-0">
              <p className="text-white font-semibold text-sm truncate max-w-sm">{brandSnippet}</p>
              <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                {platformList.map((p) => (
                  <span key={p} className="text-xs text-gray-500">{p}</span>
                ))}
                <span className="text-xs text-gray-600">·</span>
                <span className="text-xs text-gray-500">{campaign?.num_days} days</span>
              </div>
            </div>
          </div>

          {/* Schedule All */}
          <div className="flex items-center gap-3 flex-shrink-0">
            {scheduleMsg && (
              <span className="text-sm text-green-400 hidden sm:block">{scheduleMsg}</span>
            )}
            <button
              onClick={handleScheduleAll}
              disabled={!hasApproved || scheduling}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2 rounded-xl transition"
            >
              {scheduling
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : <CalendarDays className="w-4 h-4" />
              }
              Schedule All Approved
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-6">
        {/* Agent dashboard */}
        <AgentDashboard logs={campaign?.agent_logs ?? []} />

        {/* Stat bar */}
        <div className="flex flex-wrap items-center gap-6 mb-6 text-sm">
          <span className="text-gray-400">{totalCount} posts</span>
          <span className="flex items-center gap-1.5 text-green-400">
            <CheckCircle className="w-4 h-4" />
            {approvedCount} / {totalCount} approved
          </span>
          <span className="flex items-center gap-1.5 text-blue-400">
            <CalendarDays className="w-4 h-4" />
            {scheduledCount} scheduled
          </span>
          <span className="flex items-center gap-1.5 text-gray-500">
            <Clock className="w-4 h-4" />
            {totalCount - approvedCount - scheduledCount} pending
          </span>
        </div>

        {/* Post grid */}
        {posts.length === 0 ? (
          <div className="text-center py-20 text-gray-600">No posts yet.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {posts.map((post, i) => (
              <PostCard
                key={`${post?.day}-${post?.platform}-${i}`}
                post={post}
                campaignId={campaignId}
                onUpdate={refetch}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
