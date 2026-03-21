import { useState } from 'react'
import { useSavedItems } from '@/hooks/useItems'
import { ItemCard } from '@/components/items/ItemCard'
import { ItemDetail } from '@/components/items/ItemDetail'
import { cn } from '@/lib/utils'

export function ReadingListPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const { data: saved, isLoading } = useSavedItems()

  const savedIds = new Set(saved?.item_ids ?? [])
  const hasPanel = selectedId !== null

  return (
    <div className={cn(
      'flex h-[calc(100vh-3.5rem)] overflow-hidden',
    )}>

      {/* ── List ── */}
      <div className={cn(
        'flex flex-col overflow-hidden transition-all duration-300',
        hasPanel ? 'w-[42%] min-w-[280px]' : 'w-full',
      )}>
        <div className="flex-1 overflow-y-auto px-5 pt-7 pb-10">

          <div className="mb-6 fade-up">
            <p className="text-[9.5px] font-medium tracking-[0.15em] uppercase text-ink-faint mb-1">
              Your collection
            </p>
            <h1 className="font-serif text-[26px] font-normal text-ink">
              Reading list
            </h1>
            {!isLoading && saved && (
              <p className="text-[11px] text-ink-faint mt-1">
                {saved.count} {saved.count === 1 ? 'item' : 'items'} saved to study
              </p>
            )}
          </div>

          {isLoading ? (
            <div className="space-y-2.5">
              {[0, 1, 2].map(i => (
                <div key={i} className="card-kosha p-4 h-20 skeleton-warm" />
              ))}
            </div>
          ) : saved?.items.length === 0 ? (
            <div className="flex flex-col items-center py-20 gap-3 text-center">
              <svg width="28" height="28" viewBox="0 0 20 20" fill="none" className="text-ink-faint/30">
                <path d="M3 17C3 17 5 10 10 7C15 4 17 3 17 3C17 3 16 5 13 10C10 15 3 17 3 17Z" fill="currentColor"/>
              </svg>
              <p className="text-[13px] text-ink-faint">Your reading list is empty.</p>
              <p className="text-[11px] text-ink-faint/60">
                Save items from the digest to study them later.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {saved?.items.map((item, i) => (
                <ItemCard
                  key={item.id}
                  item={item}
                  isActive={item.id === selectedId}
                  isSaved={savedIds.has(item.id)}
                  onSelect={id => setSelectedId(id === selectedId ? null : id)}
                  index={i}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Reading panel ── */}
      {hasPanel && selectedId && (
        <div className="flex-1 overflow-hidden">
          <ItemDetail
            itemId={selectedId}
            isSaved={savedIds.has(selectedId)}
            onClose={() => setSelectedId(null)}
          />
        </div>
      )}
    </div>
  )
}
