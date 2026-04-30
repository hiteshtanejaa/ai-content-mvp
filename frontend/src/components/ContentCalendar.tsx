import { useState } from 'react'
import { CheckCircle, Clock, XCircle, CalendarDays, Loader2, Trash2, ArrowLeft } from 'lucide-react'
import type { Calendar, Post, PostStatus } from '../types'
import { api } from '../api'
import PostCard from './PostCard'

interface Props {
  calendar: Calendar
  onCalendarUpdate: (c: Calendar) => void
  onDelete: () => void
  onBack: () => void
}

const STATUS_COUNTS = (posts: Post[]) => ({
  total:     posts.length,
  pending:   posts.filter(p => p.status === 'pending').length,
  approved:  posts.filter(p => p.status === 'approved').length,
  rejected:  posts.filter(p => p.status === 'rejected').length,
  scheduled: posts.filter(p => p.status === 'scheduled').length,
})

export default function ContentCalendar({ calendar, onCalendarUpdate, onDelete, onBack }: Props) {
  const [activeDay, setActiveDay] = useState(1)
  const [filter, setFilter] = useState<PostStatus | 'all'>('all')

  const updatePost = (updated: Post) => {
    onCalendarUpdate({
      ...calendar,
      posts: calendar.posts.map(p => p.id === updated.id ? updated : p),
    })
  }

  const days = Array.from({ length: calendar.num_days }, (_, i) => i + 1)
  const dayPosts = calendar.posts
    .filter(p => p.day === activeDay)
    .filter(p => filter === 'all' || p.status === filter)

  const stats = STATUS_COUNTS(calendar.posts)
  const isGenerating = calendar.status === 'generating'

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="sticky top-0 z-10 bg-gray-950/90 backdrop-blur border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800 transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-bold text-white">{calendar.brand_name}</h1>
              <p className="text-xs text-gray-500">{calendar.num_days}-day calendar · {calendar.platforms?.replace(/,/g, ', ')}</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Stats */}
            <div className="hidden sm:flex items-center gap-4 text-sm">
              <span className="text-gray-400">{stats.total} posts</span>
              <span className="flex items-center gap-1 text-green-400">
                <CheckCircle className="w-4 h-4" /> {stats.approved}
              </span>
              <span className="flex items-center gap-1 text-yellow-400">
                <Clock className="w-4 h-4" /> {stats.pending}
              </span>
              <span className="flex items-center gap-1 text-blue-400">
                <CalendarDays className="w-4 h-4" /> {stats.scheduled}
              </span>
              <span className="flex items-center gap-1 text-red-400">
                <XCircle className="w-4 h-4" /> {stats.rejected}
              </span>
            </div>

            <button
              onClick={onDelete}
              className="p-2 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition"
              title="Delete calendar"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-6">
        {isGenerating && (
          <div className="mb-6 flex items-center gap-3 bg-violet-500/10 border border-violet-500/30 rounded-2xl px-5 py-4 text-violet-300">
            <Loader2 className="w-5 h-5 animate-spin flex-shrink-0" />
            <div>
              <p className="font-medium">Generating your content calendar…</p>
              <p className="text-sm text-violet-400/70 mt-0.5">
                Claude is writing captions and DALL-E is generating images. This may take 1–2 minutes.
              </p>
            </div>
          </div>
        )}

        {calendar.status === 'error' && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-2xl px-5 py-4 text-red-300">
            Generation failed. Please delete and try again.
          </div>
        )}

        {/* Day tabs */}
        <div className="flex gap-1.5 overflow-x-auto scrollbar-hide pb-2 mb-4">
          {days.map(d => {
            const dayStats = STATUS_COUNTS(calendar.posts.filter(p => p.day === d))
            const allApproved = dayStats.approved === dayStats.total && dayStats.total > 0
            return (
              <button
                key={d}
                onClick={() => setActiveDay(d)}
                className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition relative ${
                  activeDay === d
                    ? 'bg-violet-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
              >
                Day {d}
                {allApproved && (
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-gray-950" />
                )}
              </button>
            )
          })}
        </div>

        {/* Filter chips */}
        <div className="flex gap-2 mb-6">
          {(['all', 'pending', 'approved', 'rejected', 'scheduled'] as const).map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition capitalize ${
                filter === s
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {s === 'all' ? `All (${dayPosts.length + (filter !== 'all' ? calendar.posts.filter(p => p.day === activeDay && p.status !== filter).length : 0)})` : s}
            </button>
          ))}
        </div>

        {/* Post grid */}
        {calendar.posts.length === 0 && !isGenerating ? (
          <div className="text-center py-20 text-gray-600">
            <CalendarDays className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No posts yet.</p>
          </div>
        ) : dayPosts.length === 0 ? (
          <div className="text-center py-20 text-gray-600">
            <p>No {filter !== 'all' ? filter : ''} posts for Day {activeDay}.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {dayPosts.map(post => (
              <PostCard
                key={post.id}
                post={post}
                onUpdate={updatePost}
                onApprove={api.approvePost}
                onReject={api.rejectPost}
                onRegenerateCaption={api.regenerateCaption}
                onRegenerateImage={api.regenerateImage}
                onSchedule={api.schedulePost}
                onSaveCaption={(id, caption) => api.updatePost(id, { caption })}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
