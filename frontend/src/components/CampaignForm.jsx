import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'

const PLATFORMS = ['Instagram', 'LinkedIn', 'Facebook']
const DURATIONS = [7, 30]

export default function CampaignForm({ onSubmit, loading }) {
  const [brandPrompt, setBrandPrompt] = useState('')
  const [platforms, setPlatforms] = useState(['Instagram', 'LinkedIn'])
  const [numDays, setNumDays] = useState(7)

  const togglePlatform = (p) =>
    setPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    )

  const handleGenerate = () => {
    if (!brandPrompt.trim() || platforms.length === 0 || loading) return
    onSubmit({ brand_prompt: brandPrompt.trim(), platforms, num_days: numDays })
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Brand prompt */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1.5">
          Describe your brand
        </label>
        <textarea
          value={brandPrompt}
          onChange={(e) => setBrandPrompt(e.target.value)}
          rows={5}
          placeholder="e.g. EcoBrews is a sustainable coffee brand using 100% compostable packaging and single-origin beans. Our audience is eco-conscious millennials who care about ethical sourcing. Tone: warm, earthy, and inspiring."
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition resize-none text-sm"
        />
      </div>

      {/* Platforms */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Platforms</label>
        <div className="flex gap-2">
          {PLATFORMS.map((p) => (
            <div
              key={p}
              onClick={() => togglePlatform(p)}
              className={`cursor-pointer px-4 py-2 rounded-xl text-sm font-medium border transition select-none ${
                platforms.includes(p)
                  ? 'bg-violet-600 border-violet-500 text-white'
                  : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
              }`}
            >
              {p}
            </div>
          ))}
        </div>
        {platforms.length === 0 && (
          <p className="text-xs text-red-400 mt-1">Select at least one platform</p>
        )}
      </div>

      {/* Duration */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Duration</label>
        <div className="flex gap-2">
          {DURATIONS.map((d) => (
            <div
              key={d}
              onClick={() => setNumDays(d)}
              className={`cursor-pointer px-5 py-2 rounded-xl text-sm font-medium border transition select-none ${
                numDays === d
                  ? 'bg-violet-600 border-violet-500 text-white'
                  : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
              }`}
            >
              {d} days
            </div>
          ))}
        </div>
      </div>

      {/* Generate button */}
      <div
        onClick={handleGenerate}
        className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-base transition select-none ${
          loading || !brandPrompt.trim() || platforms.length === 0
            ? 'bg-violet-800 text-violet-300 cursor-not-allowed opacity-60'
            : 'bg-violet-600 hover:bg-violet-500 text-white cursor-pointer'
        }`}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Creating campaign…
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Generate Content Calendar
          </>
        )}
      </div>
    </div>
  )
}
