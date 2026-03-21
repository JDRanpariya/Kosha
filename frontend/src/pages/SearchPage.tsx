import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'
import { useSearch } from '@/hooks/useSearch'
import { useSavedItems } from '@/hooks/useItems'
import { cn } from '@/lib/utils'

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') ?? '')
  const [focused, setFocused] = useState(false)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const { data: results, isLoading, isFetching } = useSearch(query)
  const { data: saved } = useSavedItems()

  // Derived state — must live in component body, not inside JSX
  const savedIds = new Set(saved?.item_ids ?? [])

  useEffect(() => {
    const q = searchParams.get('q')
    if (q) setQuery(q)
  }, [searchParams])

  useEffect(() => { inputRef.current?.focus() }, [])

  const handleChange = (v: string) => {
    setQuery(v)
    if (v.length >= 2) setSearchParams({ q: v })
  }

  return (
    <>
      <div className="mb-8 fade-up">
        <p className="text-xs uppercase tracking-[0.15em] text-ink-faint font-medium mb-1">
          Semantic search
        </p>
        <h1 className="font-serif text-3xl font-normal text-ink">Your library</h1>
      </div>

      <div
        className={cn(
          'flex items-center gap-3 px-4 h-12 mb-8',
          'rounded-lg border bg-parchment-mid transition-all duration-200 fade-up',
          focused ? 'border-ink-faint shadow-sm' : 'border-border',
        )}
        style={{ animationDelay: '60ms', opacity: 0 }}
      >
        <Search className="h-4 w-4 text-ink-faint shrink-0" />
        <input
          ref={inputRef}
          type="search"
          placeholder="Search by topic, idea, person…"
          value={query}
          onChange={e => handleChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="flex-1 bg-transparent text-base text-ink placeholder:text-ink-faint outline-none"
        />
      </div>

      {results && query.length >= 2 && (
        <div className="section-divider mb-4" style={{ opacity: 1 }}>
          {results.count} results for "{results.query}"
        </div>
      )}

      <ItemList
        items={results?.items ?? []}
        savedIds={saved?.item_ids ?? []}
        isLoading={isLoading || isFetching}
        onSelectItem={setSelectedId}
      />

      {selectedId !== null && (
        <ItemDetail
          itemId={selectedId}
          isSaved={savedIds.has(selectedId)}
          onClose={() => setSelectedId(null)}
        />
      )}
    </>
  )
}
