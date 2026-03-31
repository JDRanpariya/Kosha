import { Bookmark, SkipForward, ExternalLink } from 'lucide-react'
import { formatRelativeTime, truncate, cn } from '@/lib/utils'
import { useFeedback } from '@/hooks/useItems'
import type { Item } from '@/types'

const SOURCE_META: Record<string, { label: string; cls: string }> = {
  rss:        { label: 'RSS',        cls: 'text-amber-700 dark:text-amber-400'   },
  substack:   { label: 'Substack',   cls: 'text-orange-700 dark:text-orange-400' },
  email_imap: { label: 'Newsletter', cls: 'text-violet-700 dark:text-violet-400' },
  arxiv:      { label: 'Paper',      cls: 'text-blue-700 dark:text-blue-400'     },
  hackernews: { label: 'HN',         cls: 'text-orange-600 dark:text-orange-400' },
  reddit:     { label: 'Reddit',     cls: 'text-red-600 dark:text-red-400'       },
  youtube:    { label: 'Video',      cls: 'text-red-600 dark:text-red-400'       },
}

interface ItemCardProps {
  item: Item
  isActive?: boolean
  isSaved?: boolean
  onSelect?: (id: number) => void
  onDismiss?: (id: number) => void   // ← new: called after optimistic removal
  index?: number
}

export function ItemCard({
  item,
  isActive = false,
  isSaved = false,
  onSelect,
  onDismiss,
  index = 0,
}: ItemCardProps) {
  const feedback = useFeedback(onDismiss)
  const meta = item.source_type ? SOURCE_META[item.source_type] : undefined
  const stagger = Math.min(index, 7)

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation()
    feedback.mutate({ item_id: item.id, type: isSaved ? 'unsave' : 'saved' })
  }

  const handleSkip = (e: React.MouseEvent) => {
    e.stopPropagation()
    feedback.mutate({ item_id: item.id, type: 'dismissed' })
  }

  return (
    <article
      onClick={() => onSelect?.(item.id)}
      className={cn(
        'card-kosha group cursor-pointer p-4 fade-up',
        `fade-up-${stagger + 1}`,
        isActive && 'border-sage bg-sage-light/30',
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          {meta && (
            <span className={cn('source-badge', meta.cls)}>
              {meta.label}
            </span>
          )}
        </div>
        <time className="text-[11px] text-ink-faint tabular-nums">
          {formatRelativeTime(item.published_at)}
        </time>
      </div>

      <h2 className={cn(
        'font-serif text-[15px] font-normal leading-snug mb-1.5 line-clamp-2',
        'transition-colors duration-150',
        isActive ? 'text-sage-dark' : 'text-ink group-hover:text-sage-dark',
      )}>
        {item.title}
      </h2>

      {item.author && (
        <p className="text-[11px] text-ink-faint mb-2">{item.author}</p>
      )}

      {!isActive && item.preview && (
        <p className="text-[12px] text-ink-mid leading-relaxed line-clamp-2 mb-3">
          {truncate(item.preview, 200)}
        </p>
      )}

      <div className={cn(
        'flex items-center gap-1 transition-opacity duration-150',
        isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100',
      )}>
        <button
          onClick={handleSave}
          disabled={feedback.isPending}
          className={cn(
            'flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors',
            isSaved
              ? 'bg-sage-light text-sage-dark font-medium'
              : 'text-ink-faint hover:text-ink hover:bg-parchment-deep',
          )}
        >
          <Bookmark className={cn('h-3 w-3', isSaved && 'fill-current')} />
          {isSaved ? 'Remove from list' : 'Save to list'}
        </button>

        {!isSaved && (
          <button
            onClick={handleSkip}
            disabled={feedback.isPending}
            className="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors"
          >
            <SkipForward className="h-3 w-3" />
            Skip
          </button>
        )}

        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={e => e.stopPropagation()}
          className="ml-auto p-1 rounded text-ink-faint hover:text-ink transition-colors"
        >
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </article>
  )
}
