import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import type { BrandInput } from '../types'

const INDUSTRIES = [
  'General', 'Fashion & Apparel', 'Food & Beverage', 'Technology', 'Health & Wellness',
  'Beauty & Cosmetics', 'Travel & Hospitality', 'Finance', 'Education', 'Real Estate',
  'Fitness', 'Entertainment', 'Non-profit', 'E-commerce', 'SaaS',
]

const TONES = [
  'Professional', 'Friendly', 'Inspirational', 'Humorous', 'Authoritative',
  'Conversational', 'Luxurious', 'Playful', 'Minimalist', 'Bold',
]

const PLATFORMS = ['Instagram', 'Twitter', 'LinkedIn', 'Facebook', 'TikTok']

interface Props {
  onSubmit: (input: BrandInput) => void
  loading: boolean
}

export default function BrandForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState<BrandInput>({
    brand_name: '',
    brand_description: '',
    industry: 'General',
    tone: 'Professional',
    platforms: ['Instagram', 'LinkedIn'],
    num_days: 7,
  })

  const togglePlatform = (p: string) => {
    setForm(f => ({
      ...f,
      platforms: f.platforms.includes(p)
        ? f.platforms.filter(x => x !== p)
        : [...f.platforms, p],
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.brand_name.trim() || !form.brand_description.trim()) return
    if (form.platforms.length === 0) return
    onSubmit(form)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-violet-600 mb-4">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AI Content Calendar</h1>
          <p className="text-gray-400">Describe your brand and get a full social media strategy in seconds.</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-2xl p-8 space-y-6 border border-gray-800">
          {/* Brand Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Brand Name</label>
            <input
              type="text"
              value={form.brand_name}
              onChange={e => setForm(f => ({ ...f, brand_name: e.target.value }))}
              placeholder="e.g. Bloom Skincare"
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
              required
            />
          </div>

          {/* Brand Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Brand Description</label>
            <textarea
              value={form.brand_description}
              onChange={e => setForm(f => ({ ...f, brand_description: e.target.value }))}
              placeholder="Tell us about your brand — what you sell, who your customers are, your mission, and what makes you unique..."
              rows={4}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition resize-none"
              required
            />
          </div>

          {/* Industry + Tone */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Industry</label>
              <select
                value={form.industry}
                onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
              >
                {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Brand Tone</label>
              <select
                value={form.tone}
                onChange={e => setForm(f => ({ ...f, tone: e.target.value }))}
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
              >
                {TONES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          {/* Platforms */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Platforms</label>
            <div className="flex flex-wrap gap-2">
              {PLATFORMS.map(p => (
                <button
                  key={p}
                  type="button"
                  onClick={() => togglePlatform(p)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition border ${
                    form.platforms.includes(p)
                      ? 'bg-violet-600 border-violet-500 text-white'
                      : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
            {form.platforms.length === 0 && (
              <p className="text-xs text-red-400 mt-1">Select at least one platform</p>
            )}
          </div>

          {/* Number of days */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Content Calendar Length: <span className="text-violet-400 font-semibold">{form.num_days} days</span>
            </label>
            <input
              type="range"
              min={3}
              max={14}
              value={form.num_days}
              onChange={e => setForm(f => ({ ...f, num_days: Number(e.target.value) }))}
              className="w-full accent-violet-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>3 days</span>
              <span>14 days</span>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || form.platforms.length === 0}
            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-xl transition flex items-center justify-center gap-2 text-base"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating Calendar…
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Content Calendar
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
