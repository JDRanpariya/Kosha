import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useTeachSignal } from '@/hooks/useItems'
import type { ItemDetail } from '@/types'

// ── Tag extraction ────────────────────────────────────────────────────────
// In Phase 1 these are heuristically derived from item metadata.
// In Phase 2 the backend will generate them from content via LLM.

function deriveDefaultTags(item: ItemDetail): string[] {
  const tags: string[] = []
  const meta = item.metadata ?? {}
  const type = meta.source_type as string | undefined

  // Source-type tags
  if (type === 'arxiv') tags.push('New research', 'Technical depth')
  if (type === 'hackernews' || type === 'reddit') tags.push('Community discussion', 'Practical application')
  if (type === 'youtube' || type === 'youtube_subscriptions') tags.push('Visual explanation', 'Talk / lecture')
  if (type === 'spotify') tags.push('Long-form audio', 'Conversation')
  if (type === 'rss' || type === 'substack') tags.push('Essay / opinion', 'Long read')

  // Generic intellectual hooks — always available
  tags.push(
    'Challenges my assumptions',
    'Cross-domain connection',
    'Useful technique',
    'Sparks curiosity',
  )

  // Deduplicate and cap at 6
  return [...new Set(tags)].slice(0, 6)
}

interface TeachStripProps {
  item: ItemDetail
}

type StripState = 'idle' | 'selecting' | 'done'

export function TeachStrip({ item }: TeachStripProps) {
  const [state, setState] = useState<StripState>('idle')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const teach = useTeachSignal()

  const tags = deriveDefaultTags(item)

  const toggle = (tag: string) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(tag) ? next.delete(tag) : next.add(tag)
      return next
    })
    if (state === 'idle') setState('selecting')
  }

  const handleSubmit = () => {
    if (selected.size === 0) return
    teach.mutate(
      { item_id: item.id, selected_tags: [...selected] },
      { onSuccess: () => setState('done') },
    )
  }

  const handleSkip = () => setState('done')

  if (state === 'done') {
    return (
      <div className="border-t border-border px-5 py-3 flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-sage" />
        <p className="text-[11px] text-ink-faint">
          Signal recorded — helps Kosha learn your interests.
        </p>
      </div>
    )
  }

  return (
    <div className="border-t border-border bg-parchment-mid px-5 py-4 shrink-0">
      {/* Label */}
      <p className="text-[9.5px] font-medium tracking-[0.1em] uppercase text-ink-faint mb-2.5">
        What draws you to this?
      </p>

      {/* Tag chips */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {tags.map(tag => (
          <button
            key={tag}
            onClick={() => toggle(tag)}
            className={cn(
              'px-2.5 py-1 rounded text-[11px] border transition-all duration-120 font-sans',
              selected.has(tag)
                ? 'bg-sage-light border-sage text-sage-dark font-medium'
                : 'bg-parchment border-border text-ink-mid hover:border-ink-faint hover:text-ink',
            )}
          >
            {tag}
          </button>
        ))}
      </div>

      {/* Actions — only show once something is selected */}
      <div className={cn(
        'flex items-center gap-2 transition-opacity duration-200',
        selected.size > 0 ? 'opacity-100' : 'opacity-0 pointer-events-none',
      )}>
        <button
          onClick={handleSubmit}
          disabled={teach.isPending}
          className="px-3 py-1.5 rounded text-[11px] bg-ink text-parchment hover:bg-ink-mid transition-colors disabled:opacity-40"
        >
          {teach.isPending ? 'Saving…' : 'Record signal'}
        </button>
        <button
          onClick={handleSkip}
          className="text-[11px] text-ink-faint hover:text-ink transition-colors"
        >
          Skip
        </button>
        <p className="ml-auto text-[10px] text-ink-faint/60 italic">
          Trains the preference model
        </p>
      </div>
    </div>
  )
}
