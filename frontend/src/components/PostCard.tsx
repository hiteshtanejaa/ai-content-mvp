import { useState } from 'react'
import {
  Check, X, RefreshCw, Edit3, Image as ImageIcon,
  Calendar, ChevronDown, ChevronUp, Loader2,
} from 'lucide-react'
import type { Post, PostStatus } from '../types'

const PLATFORM_STYLES: Record<string, string> = {
  Instagram: 'bg-gradient-to-r from-purple-500 to-pink-500',
  Twitter:   'bg-sky-500',
  LinkedIn:  'bg-blue-700',
  Facebook:  'bg-blue-600',
  TikTok:    'bg-gray-900 border border-gray-600',
}

const STATUS_STYLES: Record<PostStatus, string> = {
  pending:   'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  approved:  'bg-green-500/10 text-green-400 border-green-500/30',
  rejected:  'bg-red-500/10 text-red-400 border-red-500/30',
  scheduled: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
}

interface Props {
  post: Post
  onUpdate: (updated: Post) => void
  onApprove: (id: string) => Promise<Post>
  onReject: (id: string) => Promise<Post>
  onRegenerateCaption: (id: string) => Promise<Post>
  onRegenerateImage: (id: string) => Promise<Post>
  onSchedule: (id: string) => Promise<Post>
  onSaveCaption: (id: string, caption: string) => Promise<Post>
}

export default function PostCard({
  post, onUpdate, onApprove, onReject,
  onRegenerateCaption, onRegenerateImage, onSchedule, onSaveCaption,
}: Props) {
  const [editing, setEditing] = useState(false)
  const [editedCaption, setEditedCaption] = useState(post.caption ?? '')
  const [showPrompt, setShowPrompt] = useState(false)
  const [imgError, setImgError] = useState(false)
  const [busy, setBusy] = useState<string | null>(null)  // which action is running

  const run = async (key: string, fn: () => Promise<Post>) => {
    setBusy(key)
    try {
      const updated = await fn()
      onUpdate(updated)
      if (key === 'caption') setEditedCaption(updated.caption ?? '')
    } finally {
      setBusy(null)
    }
  }

  const saveEdit = () => {
    run('save', () => onSaveCaption(post.id, editedCaption))
    setEditing(false)
  }

  const platformStyle = PLATFORM_STYLES[post.platform] ?? 'bg-gray-600'

  return (
    <div className={`bg-gray-900 border rounded-2xl overflow-hidden transition-all ${
      post.status === 'rejected' ? 'border-red-900/50 opacity-60' : 'border-gray-800 hover:border-gray-700'
    }`}>
      {/* Platform + Status header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <span className={`text-xs font-bold px-2.5 py-1 rounded-lg text-white ${platformStyle}`}>
          {post.platform}
        </span>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-lg border ${STATUS_STYLES[post.status]}`}>
          {post.status.charAt(0).toUpperCase() + post.status.slice(1)}
        </span>
      </div>

      {/* Image */}
      <div className="relative bg-gray-800 aspect-square">
        {post.image_url && !imgError ? (
          <img
            src={post.image_url}
            alt="Generated post visual"
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-600">
            <ImageIcon className="w-10 h-10" />
            <span className="text-xs text-center px-4">
              {post.image_url ? 'Image unavailable' : 'No image generated'}
            </span>
          </div>
        )}

        {/* Regenerate image button overlay */}
        {post.status !== 'scheduled' && (
          <button
            onClick={() => run('image', () => onRegenerateImage(post.id))}
            disabled={busy !== null}
            title="Regenerate image"
            className="absolute bottom-2 right-2 p-2 rounded-xl bg-black/60 hover:bg-black/80 text-white disabled:opacity-50 transition backdrop-blur-sm"
          >
            {busy === 'image'
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <ImageIcon className="w-4 h-4" />
            }
          </button>
        )}
      </div>

      {/* Caption */}
      <div className="p-4 space-y-3">
        {editing ? (
          <div className="space-y-2">
            <textarea
              value={editedCaption}
              onChange={e => setEditedCaption(e.target.value)}
              rows={5}
              className="w-full bg-gray-800 border border-violet-500 rounded-xl px-3 py-2 text-sm text-white resize-none focus:outline-none focus:ring-1 focus:ring-violet-400"
            />
            <div className="flex gap-2">
              <button
                onClick={saveEdit}
                disabled={busy === 'save'}
                className="flex-1 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-xs font-medium py-1.5 rounded-lg transition flex items-center justify-center gap-1"
              >
                {busy === 'save' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                Save
              </button>
              <button
                onClick={() => { setEditing(false); setEditedCaption(post.caption ?? '') }}
                className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium py-1.5 rounded-lg transition"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-300 leading-relaxed line-clamp-4">
            {post.caption ?? <span className="text-gray-600 italic">No caption</span>}
          </p>
        )}

        {/* Image prompt toggle */}
        {post.image_prompt && (
          <button
            onClick={() => setShowPrompt(v => !v)}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-400 transition"
          >
            {showPrompt ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            Image prompt
          </button>
        )}
        {showPrompt && post.image_prompt && (
          <p className="text-xs text-gray-500 italic bg-gray-800/60 rounded-lg px-3 py-2 leading-relaxed">
            {post.image_prompt}
          </p>
        )}

        {/* Actions */}
        {post.status !== 'scheduled' && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {post.status !== 'approved' && post.status !== 'rejected' && (
              <button
                onClick={() => run('approve', () => onApprove(post.id))}
                disabled={busy !== null}
                className="flex items-center gap-1 px-3 py-1.5 bg-green-600/20 hover:bg-green-600/30 text-green-400 text-xs font-medium rounded-lg transition disabled:opacity-50"
              >
                {busy === 'approve' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                Approve
              </button>
            )}
            {post.status !== 'rejected' && (
              <button
                onClick={() => run('reject', () => onReject(post.id))}
                disabled={busy !== null}
                className="flex items-center gap-1 px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 text-xs font-medium rounded-lg transition disabled:opacity-50"
              >
                {busy === 'reject' ? <Loader2 className="w-3 h-3 animate-spin" /> : <X className="w-3 h-3" />}
                Reject
              </button>
            )}
            {post.status !== 'rejected' && (
              <>
                <button
                  onClick={() => setEditing(true)}
                  disabled={busy !== null}
                  className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition disabled:opacity-50"
                >
                  <Edit3 className="w-3 h-3" /> Edit
                </button>
                <button
                  onClick={() => run('caption', () => onRegenerateCaption(post.id))}
                  disabled={busy !== null}
                  className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded-lg transition disabled:opacity-50"
                >
                  {busy === 'caption' ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                  Regen
                </button>
              </>
            )}
            {post.status === 'approved' && (
              <button
                onClick={() => run('schedule', () => onSchedule(post.id))}
                disabled={busy !== null}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 text-xs font-medium rounded-lg transition disabled:opacity-50"
              >
                {busy === 'schedule' ? <Loader2 className="w-3 h-3 animate-spin" /> : <Calendar className="w-3 h-3" />}
                Schedule
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
