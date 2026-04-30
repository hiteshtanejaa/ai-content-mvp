import { useState } from 'react'
import { Check, RefreshCw, Image, Loader2 } from 'lucide-react'
import StatusBadge from './StatusBadge'
import { updatePost, regeneratePost } from '../api'

const PLATFORM_COLORS = {
  Instagram: 'bg-gradient-to-r from-purple-500 to-pink-500 text-white',
  LinkedIn:  'bg-blue-700 text-white',
  Facebook:  'bg-blue-600 text-white',
  Twitter:   'bg-sky-500 text-white',
  TikTok:    'bg-gray-800 text-white border border-gray-600',
}

export default function PostCard({ post, campaignId, onUpdate }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(post?.caption ?? '')
  const [saving, setSaving] = useState(false)
  const [regenerating, setRegenerating] = useState(false)
  const [imgError, setImgError] = useState(false)

  const status = post?.status ?? 'draft'
  const isScheduled = status === 'scheduled'
  const isApproved  = status === 'approved'

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await updatePost(campaignId, post.day, {
        caption: draft,
        status: 'approved',
      })
      onUpdate?.(updated)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleApprove = async () => {
    const updated = await updatePost(campaignId, post.day, { status: 'approved' })
    onUpdate?.(updated)
  }

  const handleRegenerate = async () => {
    setRegenerating(true)
    try {
      await regeneratePost(campaignId, post.day)
      onUpdate?.()
    } finally {
      setRegenerating(false)
    }
  }

  return (
    <div
      className={`bg-gray-900 border rounded-2xl overflow-hidden flex flex-col transition-all ${
        isApproved  ? 'border-l-4 border-l-green-500 border-t-gray-800 border-r-gray-800 border-b-gray-800' :
        isScheduled ? 'border-gray-800 opacity-50' :
                      'border-gray-800 hover:border-gray-700'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2.5 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 font-medium">Day {post?.day ?? '?'}</span>
          <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${PLATFORM_COLORS[post?.platform] ?? 'bg-gray-700 text-gray-300'}`}>
            {post?.platform ?? '—'}
          </span>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* Content type label */}
      <div className="px-3 pt-2 pb-0">
        <span className="text-xs text-gray-600 uppercase tracking-wide">{post?.content_type ?? 'image'}</span>
      </div>

      {/* Image */}
      <div className="relative mx-3 mt-2 rounded-xl overflow-hidden bg-gray-800 aspect-square">
        {post?.image_url && !imgError ? (
          <img
            src={post.image_url}
            alt="Generated visual"
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-600 gap-2">
            <Image className="w-8 h-8" />
            <span className="text-xs">No image</span>
          </div>
        )}
      </div>

      {/* Caption */}
      <div className="px-3 py-3 flex-1 flex flex-col gap-2">
        {editing ? (
          <>
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              rows={5}
              className="w-full bg-gray-800 border border-violet-500 rounded-xl px-3 py-2 text-sm text-white resize-none focus:outline-none focus:ring-1 focus:ring-violet-400"
            />
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-xs font-medium py-1.5 rounded-lg transition flex items-center justify-center gap-1"
              >
                {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                Save & Approve
              </button>
              <button
                onClick={() => { setEditing(false); setDraft(post?.caption ?? '') }}
                className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium py-1.5 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </>
        ) : (
          <p
            onClick={() => { if (!isScheduled) { setEditing(true); setDraft(post?.caption ?? '') } }}
            className={`text-sm text-gray-300 leading-relaxed line-clamp-4 ${!isScheduled ? 'cursor-text hover:text-white transition-colors' : ''}`}
            title={isScheduled ? '' : 'Click to edit'}
          >
            {post?.caption || <span className="text-gray-600 italic">No caption</span>}
          </p>
        )}

        {/* Hashtags */}
        {(post?.hashtags?.length ?? 0) > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {post.hashtags.map((tag) => (
              <span key={tag} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Action buttons */}
        {!editing && !isScheduled && (
          <div className="flex gap-1.5 pt-1">
            {!isApproved && (
              <button
                onClick={handleApprove}
                className="flex items-center gap-1 px-3 py-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-400 text-xs font-medium rounded-lg transition"
              >
                <Check className="w-3 h-3" /> Approve
              </button>
            )}
            <button
              onClick={handleRegenerate}
              disabled={regenerating}
              className="flex items-center gap-1 px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 text-xs font-medium rounded-lg transition disabled:opacity-50"
            >
              {regenerating
                ? <Loader2 className="w-3 h-3 animate-spin" />
                : <RefreshCw className="w-3 h-3" />
              }
              Regenerate
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
