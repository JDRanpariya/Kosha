import { useState, useMemo } from 'react'
import { useDailyDigest, useSavedItems } from '@/hooks/useItems'
import { ItemCard } from '@/components/items/ItemCard'
import { ItemDetail } from '@/components/items/ItemDetail'
import { cn } from '@/lib/utils'
import type { Item } from '@/types'

// ── Source grouping ───────────────────────────────────────────────────────

const SOURCE_GROUPS: Array<{
  key: string
  label: string
  types: string[]
}> = [
  { key: 'papers',    label: 'Research papers',     types: ['arxiv'] },
  { key: 'essays',    label: 'Essays & newsletters', types: ['rss', 'substack', 'email_imap'] },
  { key: 'social',    label: 'Discussions',          types: ['hackernews', 'reddit'] },
  { key: 'videos',    label: 'Videos & podcasts',    types: ['youtube', 'youtube_subscriptions', 'spotify'] },
  { key: 'dev',       label: 'Dev & open source',    types: ['github'] },
]

function groupItems(items: Item[]) {
  const grouped: Record<string, Item[]> = {}
  const used = new Set<number>()

  for (const group of SOURCE_GROUPS) {
    const matched = items.filter(
      it => !used.has(it.id) && group.types.includes(it.source_type ?? '')
    )
    if (matched.length > 0) {
      grouped[group.key] = matched
      matched.forEach(it => used.add(it.id))
    }
  }

  // Anything that didn't match a group goes into 'other'
  const other = items.filter(it => !used.has(it.id))
  if (other.length > 0) grouped['other'] = other

  return grouped
}

// ── Filter pill ───────────────────────────────────────────────────────────

interface FilterPillProps {
  label: string
  count: number
  active: boolean
  onClick: () => void
}

function FilterPill({ label, count, active, onClick }: FilterPillProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-3 py-1 rounded-full text-[11px] border transition-all duration-150',
        active
          ? 'bg-ink text-parchment border-ink font-medium'
          : 'border-border text-ink-mid hover:border-ink-faint hover:text-ink',
      )}
    >
      {label}
      <span className={cn(
        'ml-1.5 opacity-60 text-[10px]',
        active && 'opacity-80',
      )}>
        {count}
      </span>
    </button>
  )
}

// ── Section divider ───────────────────────────────────────────────────────

function SectionDivider({ label }: { label: string }) {
  return (
    <div className="section-divider mt-5 mb-3" style={{ opacity: 1 }}>
      {label}
    </div>
  )
}

// ── Skeleton list ─────────────────────────────────────────────────────────

function SkeletonList() {
  return (
    <div className="space-y-2.5">
      {[0, 1, 2, 3, 4].map(i => (
        <div
          key={i}
          className="card-kosha p-4 space-y-2.5 fade-up"
          style={{ animationDelay: `${i * 60}ms`, opacity: 0 }}
        >
          <div className="flex justify-between">
            <div className="skeleton-warm h-3.5 w-14 rounded-full" />
            <div className="skeleton-warm h-3 w-16" />
          </div>
          <div className="skeleton-warm h-4 w-3/4" />
          <div className="skeleton-warm h-3.5 w-1/3" />
          <div className="space-y-1.5">
            <div className="skeleton-warm h-3 w-full" />
            <div className="skeleton-warm h-3 w-4/5" />
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────

function EmptyDigest() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <svg width="28" height="28" viewBox="0 0 20 20" fill="none" className="text-ink-faint/30">
        <path d="M3 17C3 17 5 10 10 7C15 4 17 3 17 3C17 3 16 5 13 10C10 15 3 17 3 17Z" fill="currentColor"/>
      </svg>
      <p className="text-[13px] text-ink-faint">Nothing new today.</p>
      <p className="text-[11px] text-ink-faint/60">
        Add sources or trigger a sync to pull fresh content.
      </p>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────

export function DigestPage() {
  const [activeFilter, setActiveFilter] = useState<string>('all')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const {
    data,
    isLoading,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useDailyDigest()

  const { data: saved } = useSavedItems()

  const allItems = data?.pages.flatMap(p => p.items) ?? []
  const total = data?.pages[0]?.total ?? 0
  const savedIds = new Set(saved?.item_ids ?? [])

  // Build filter options from what's actually in the digest
  const filterOptions = useMemo(() => {
    const counts: Record<string, number> = { all: allItems.length }
    for (const group of SOURCE_GROUPS) {
      const n = allItems.filter(it => group.types.includes(it.source_type ?? '')).length
      if (n > 0) counts[group.key] = n
    }
    return counts
  }, [allItems])

  // Apply filter
  const filteredItems = useMemo(() => {
    if (activeFilter === 'all') return allItems
    const group = SOURCE_GROUPS.find(g => g.key === activeFilter)
    if (!group) return allItems
    return allItems.filter(it => group.types.includes(it.source_type ?? ''))
  }, [allItems, activeFilter])

  // Group for display
  const grouped = useMemo(() => {
    if (activeFilter !== 'all') {
      // When filtered, don't show section headers — just a flat list
      return null
    }
    return groupItems(filteredItems)
  }, [filteredItems, activeFilter])

  // Date header
  const now = new Date()
  const day  = now.toLocaleDateString('en-US', { weekday: 'long' })
  const date = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })

  const selectedItem = allItems.find(it => it.id === selectedId)
  const hasPanel = selectedId !== null

  return (
    <div className={cn(
      'flex h-[calc(100vh-3.5rem)] overflow-hidden',
      // Remove the outer padding when in split-panel mode — the panel handles its own
    )}>

      {/* ── List column ── */}
      <div className={cn(
        'flex flex-col overflow-hidden transition-all duration-300',
        hasPanel ? 'w-[42%] min-w-[280px]' : 'w-full',
      )}>
        {/* Header area — scrolls away */}
        <div className="flex-1 overflow-y-auto px-5 pt-7 pb-10">

          {/* Date heading */}
          <div className="mb-5 fade-up">
            <p className="text-[9.5px] font-medium tracking-[0.15em] uppercase text-ink-faint mb-1">
              {day}
            </p>
            <h1 className="font-serif text-[26px] font-normal text-ink leading-none">
              {date}
            </h1>
            {!isLoading && (
              <p className="text-[11px] text-ink-faint mt-1">
                {total} new items
              </p>
            )}
          </div>

          {/* Filter pills */}
          {!isLoading && allItems.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4 fade-up" style={{ animationDelay: '60ms', opacity: 0 }}>
              <FilterPill
                label="All"
                count={filterOptions.all ?? 0}
                active={activeFilter === 'all'}
                onClick={() => setActiveFilter('all')}
              />
              {SOURCE_GROUPS.map(g =>
                filterOptions[g.key] ? (
                  <FilterPill
                    key={g.key}
                    label={g.label.split(' ')[0]} // Just "Research", "Essays", etc.
                    count={filterOptions[g.key]}
                    active={activeFilter === g.key}
                    onClick={() => setActiveFilter(g.key)}
                  />
                ) : null
              )}
            </div>
          )}

          {/* Content */}
          {isLoading ? (
            <SkeletonList />
          ) : allItems.length === 0 ? (
            <EmptyDigest />
          ) : grouped ? (
            // Grouped view (all filter)
            Object.entries(grouped).map(([key, items]) => {
              const group = SOURCE_GROUPS.find(g => g.key === key)
              return (
                <div key={key}>
                  <SectionDivider label={group?.label ?? key} />
                  <div className="space-y-2">
                    {items.map((item, i) => (
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
                </div>
              )
            })
          ) : (
            // Flat filtered view
            <div className="space-y-2">
              {filteredItems.map((item, i) => (
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

          {/* Load more */}
          {hasNextPage && (
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                className="px-4 py-2 rounded-md border border-border text-[12px] text-ink-mid hover:text-ink hover:bg-parchment-deep transition-colors disabled:opacity-40"
              >
                {isFetchingNextPage ? 'Loading…' : 'Load more'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Reading panel — inline split, not a modal ── */}
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
