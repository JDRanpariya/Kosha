import { ItemCard } from './ItemCard'
import { cn } from '@/lib/utils'
import type { Item } from '@/types'

function SkeletonCard({ delay = 0 }: { delay?: number }) {
  return (
    <div
      className="card-kosha p-5 space-y-3 fade-up"
      style={{ animationDelay: `${delay * 60}ms`, opacity: 0 }}
    >
      <div className="flex justify-between items-center">
        <div className="skeleton-warm h-4 w-16 rounded-full" />
        <div className="skeleton-warm h-3 w-20" />
      </div>
      <div className="skeleton-warm h-5 w-3/4" />
      <div className="skeleton-warm h-4 w-1/3" />
      <div className="space-y-2 pt-1">
        <div className="skeleton-warm h-3 w-full" />
        <div className="skeleton-warm h-3 w-5/6" />
        <div className="skeleton-warm h-3 w-4/6" />
      </div>
    </div>
  )
}

interface ItemListProps {
  items: Item[]
  savedIds?: number[]
  isLoading?: boolean
  onSelectItem?: (id: number) => void
}

export function ItemList({ items, savedIds = [], isLoading, onSelectItem }: ItemListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[0, 1, 2, 3, 4].map(i => (
          <SkeletonCard key={i} delay={i} />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-3 text-center">
        {/* A small leaf illustration */}
        <svg width="32" height="32" viewBox="0 0 20 20" fill="none" className="text-ink-faint/40">
          <path
            d="M3 17C3 17 5 10 10 7C15 4 17 3 17 3C17 3 16 5 13 10C10 15 3 17 3 17Z"
            fill="currentColor"
          />
        </svg>
        <p className="text-sm text-ink-faint">Nothing here yet.</p>
        <p className="text-xs text-ink-faint/60">Add sources and trigger an ingestion.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <ItemCard
          key={item.id}
          item={item}
          isSaved={savedIds.includes(item.id)}
          onSelect={onSelectItem}
          index={i}
        />
      ))}
    </div>
  )
}
