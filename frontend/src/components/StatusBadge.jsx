import { Loader2 } from 'lucide-react'

const STYLES = {
  draft:      'bg-gray-700 text-gray-300',
  approved:   'bg-green-500/20 text-green-400 border border-green-500/40',
  regenerate: 'bg-amber-500/20 text-amber-400 border border-amber-500/40',
  scheduled:  'bg-blue-500/20 text-blue-400 border border-blue-500/40',
}

const LABELS = {
  draft:      'Draft',
  approved:   'Approved',
  regenerate: 'Regenerating',
  scheduled:  'Scheduled',
}

export default function StatusBadge({ status }) {
  const s = status?.toLowerCase() ?? 'draft'
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${STYLES[s] ?? STYLES.draft}`}>
      {s === 'regenerate' && <Loader2 className="w-3 h-3 animate-spin" />}
      {LABELS[s] ?? s}
    </span>
  )
}
