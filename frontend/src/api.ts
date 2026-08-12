import type { Calendar, BrandInput, Post } from './types'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText)
    throw new Error(msg || `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  createCalendar: (input: BrandInput) =>
    req<Calendar>('/api/calendars', { method: 'POST', body: JSON.stringify(input) }),

  listCalendars: () => req<Calendar[]>('/api/calendars'),

  getCalendar: (id: string) => req<Calendar>(`/api/calendars/${id}`),

  deleteCalendar: (id: string) => req<void>(`/api/calendars/${id}`, { method: 'DELETE' }),

  updatePost: (id: string, data: { caption?: string; status?: string }) =>
    req<Post>(`/api/posts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  approvePost: (id: string) =>
    req<Post>(`/api/posts/${id}/approve`, { method: 'POST' }),

  rejectPost: (id: string) =>
    req<Post>(`/api/posts/${id}/reject`, { method: 'POST' }),

  regenerateCaption: (id: string) =>
    req<Post>(`/api/posts/${id}/regenerate-caption`, { method: 'POST' }),

  regenerateImage: (id: string) =>
    req<Post>(`/api/posts/${id}/regenerate-image`, { method: 'POST' }),

  schedulePost: (id: string) =>
    req<Post>(`/api/posts/${id}/schedule`, { method: 'POST' }),
}
