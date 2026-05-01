import { useState } from 'react'
import { CheckCircle, Loader2, Clock, AlertCircle, ChevronDown, ChevronUp, Bot } from 'lucide-react'

const AGENT_META = {
  strategy:  { label: 'Strategy Agent',  desc: 'Analyses brand, builds visual style guide, plans content calendar' },
  content:   { label: 'Content Agent',   desc: 'Writes captions, generates hashtags and DALL-E images' },
  scheduler: { label: 'Scheduler Agent', desc: 'Publishes approved posts to social platforms' },
}

const STATUS_ICON = {
  running: <Loader2 className="w-4 h-4 animate-spin text-violet-400" />,
  done:    <CheckCircle className="w-4 h-4 text-green-400" />,
  error:   <AlertCircle className="w-4 h-4 text-red-400" />,
  waiting: <Clock className="w-4 h-4 text-gray-500" />,
}

const STATUS_BG = {
  running: 'border-violet-500/40 bg-violet-500/5',
  done:    'border-green-500/30 bg-green-500/5',
  error:   'border-red-500/30 bg-red-500/5',
  waiting: 'border-gray-700 bg-gray-900',
}

function AgentCard({ agentKey, logs }) {
  const meta = AGENT_META[agentKey] ?? { label: agentKey, desc: '' }
  const agentLogs = (logs ?? []).filter((l) => l.agent === agentKey)
  const latest = agentLogs[agentLogs.length - 1]
  const status = latest?.status ?? 'waiting'

  return (
    <div className={`rounded-xl border p-4 transition-all ${STATUS_BG[status] ?? STATUS_BG.waiting}`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex-shrink-0">{STATUS_ICON[status] ?? STATUS_ICON.waiting}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold text-white">{meta.label}</p>
            <span className={`text-xs capitalize px-2 py-0.5 rounded-full ${
              status === 'running' ? 'bg-violet-500/20 text-violet-300' :
              status === 'done'    ? 'bg-green-500/20 text-green-300' :
              status === 'error'   ? 'bg-red-500/20 text-red-300' :
                                    'bg-gray-700 text-gray-400'
            }`}>{status}</span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">{meta.desc}</p>
          {latest?.message && (
            <p className="text-xs text-gray-300 mt-2 leading-relaxed">{latest.message}</p>
          )}
          {latest?.ts && (
            <p className="text-xs text-gray-600 mt-1">
              {new Date(latest.ts).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AgentDashboard({ logs }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="mb-6 bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-3.5 text-left hover:bg-gray-800/50 transition"
      >
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-white">Agent Dashboard</span>
          <span className="text-xs text-gray-500">{Object.keys(AGENT_META).length} agents</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      {open && (
        <div className="px-4 pb-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
          {Object.keys(AGENT_META).map((key) => (
            <AgentCard key={key} agentKey={key} logs={logs} />
          ))}
        </div>
      )}
    </div>
  )
}
