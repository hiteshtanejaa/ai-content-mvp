import { useState, useEffect, useCallback, useRef } from 'react'
import { Sparkles, CalendarDays, Trash2, Clock, ChevronRight, AlertCircle } from 'lucide-react'
import { api } from './api'
import type { Calendar, BrandInput } from './types'
import BrandForm from './components/BrandForm'
import ContentCalendar from './components/ContentCalendar'

type View = 'home' | 'form' | 'calendar'

export default function App() {
  const [view, setView] = useState<View>('home')
  const [calendars, setCalendars] = useState<Calendar[]>([])
  const [activeCalendar, setActiveCalendar] = useState<Calendar | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const loadCalendars = useCallback(async () => {
    try {
      const list = await api.listCalendars()
      setCalendars(list)
    } catch {
      // silently ignore list errors
    }
  }, [])

  useEffect(() => {
    loadCalendars()
  }, [loadCalendars])

  // Poll active calendar while it's still generating
  useEffect(() => {
    if (!activeCalendar || activeCalendar.status === 'ready' || activeCalendar.status === 'error') {
      if (pollRef.current) clearInterval(pollRef.current)
      return
    }

    pollRef.current = setInterval(async () => {
      try {
        const updated = await api.getCalendar(activeCalendar.id)
        setActiveCalendar(updated)
        setCalendars(prev => prev.map(c => c.id === updated.id ? updated : c))
        if (updated.status === 'ready' || updated.status === 'error') {
          clearInterval(pollRef.current!)
        }
      } catch { /* ignore */ }
    }, 3000)

    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [activeCalendar?.id, activeCalendar?.status])

  const handleCreate = async (input: BrandInput) => {
    setSubmitting(true)
    setError(null)
    try {
      const cal = await api.createCalendar(input)
      setCalendars(prev => [cal, ...prev])
      setActiveCalendar(cal)
      setView('calendar')
    } catch (e: any) {
      setError(e.message ?? 'Failed to create calendar')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this calendar and all its posts?')) return
    try {
      await api.deleteCalendar(id)
      setCalendars(prev => prev.filter(c => c.id !== id))
      if (activeCalendar?.id === id) {
        setActiveCalendar(null)
        setView('home')
      }
    } catch (e: any) {
      alert(e.message)
    }
  }

  const openCalendar = async (id: string) => {
    const full = await api.getCalendar(id)
    setActiveCalendar(full)
    setView('calendar')
  }

  // ── Views ────────────────────────────────────────────────────────────────

  if (view === 'form') {
    return (
      <BrandForm
        onSubmit={handleCreate}
        loading={submitting}
      />
    )
  }

  if (view === 'calendar' && activeCalendar) {
    return (
      <ContentCalendar
        calendar={activeCalendar}
        onCalendarUpdate={updated => {
          setActiveCalendar(updated)
          setCalendars(prev => prev.map(c => c.id === updated.id ? updated : c))
        }}
        onDelete={() => handleDelete(activeCalendar.id)}
        onBack={() => setView('home')}
      />
    )
  }

  // Home / dashboard
  return (
    <div className="min-h-screen p-6 max-w-5xl mx-auto">
      {/* Hero */}
      <div className="text-center py-16">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-violet-600 mb-5">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-3">AI Content Calendar</h1>
        <p className="text-gray-400 text-lg mb-8 max-w-xl mx-auto">
          Describe your brand, get a full multi-day social media strategy with AI-written captions and generated images.
        </p>
        <button
          onClick={() => { setError(null); setView('form') }}
          className="bg-violet-600 hover:bg-violet-500 text-white font-semibold px-8 py-3.5 rounded-xl transition inline-flex items-center gap-2 text-base"
        >
          <Sparkles className="w-5 h-5" />
          Create New Calendar
        </button>
        {error && (
          <div className="mt-4 flex items-center justify-center gap-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}
      </div>

      {/* Past calendars */}
      {calendars.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Your Calendars
          </h2>
          <div className="space-y-3">
            {calendars.map(cal => (
              <div
                key={cal.id}
                className="bg-gray-900 border border-gray-800 rounded-2xl px-5 py-4 flex items-center justify-between gap-4 hover:border-gray-700 transition"
              >
                <button
                  className="flex items-center gap-4 flex-1 text-left"
                  onClick={() => openCalendar(cal.id)}
                >
                  <div className="w-10 h-10 rounded-xl bg-violet-600/20 flex items-center justify-center flex-shrink-0">
                    <CalendarDays className="w-5 h-5 text-violet-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{cal.brand_name}</p>
                    <p className="text-sm text-gray-500">
                      {cal.num_days} days · {cal.platforms?.replace(/,/g, ', ')}
                    </p>
                  </div>
                  <div className="ml-auto mr-4 hidden sm:block">
                    {cal.status === 'generating' ? (
                      <span className="flex items-center gap-1.5 text-xs text-yellow-400 bg-yellow-500/10 border border-yellow-500/30 px-2.5 py-1 rounded-lg">
                        <Clock className="w-3 h-3" /> Generating…
                      </span>
                    ) : cal.status === 'error' ? (
                      <span className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 px-2.5 py-1 rounded-lg">Error</span>
                    ) : (
                      <span className="text-xs text-green-400 bg-green-500/10 border border-green-500/30 px-2.5 py-1 rounded-lg">
                        {cal.posts.length} posts
                      </span>
                    )}
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
                </button>

                <button
                  onClick={e => { e.stopPropagation(); handleDelete(cal.id) }}
                  className="p-2 rounded-xl text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition flex-shrink-0"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {calendars.length === 0 && (
        <div className="text-center py-8 text-gray-700">
          <p className="text-sm">No calendars yet. Create your first one above.</p>
        </div>
      )}
    </div>
  )
}
