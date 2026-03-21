import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'
import { useSearch } from '@/hooks/useSearch'
import { useSavedItems } from '@/hooks/useItems'

export function SearchPage() {
    const [searchParams, setSearchParams] = useSearchParams()
    const initialQuery = searchParams.get('q') ?? ''
    const [query, setQuery] = useState(initialQuery)
    const [selectedId, setSelectedId] = useState<number | null>(null)

    const { data: results, isLoading, isFetching } = useSearch(query)
    const { data: saved } = useSavedItems()

    useEffect(() => {
        const q = searchParams.get('q')
        if (q) setQuery(q)
    }, [searchParams])

    const handleSearch = (value: string) => {
        setQuery(value)
        if (value.length >= 2) {
            setSearchParams({ q: value })
        }
    }

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold mb-4">Semantic Search</h1>
                <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search your content library..."
                        className="pl-10"
                        value={query}
                        onChange={(e) => handleSearch(e.target.value)}
                    />
                </div>
                {results && (
                    <p className="text-sm text-muted-foreground mt-2">
                        Found {results.count} results for "{results.query}"
                    </p>
                )}
            </div>

            <ItemList
                items={results?.items ?? []}
                savedIds={saved?.item_ids ?? []}
                isLoading={isLoading || isFetching}
                onSelectItem={setSelectedId}
            />

            {selectedId && <ItemDetail itemId={selectedId} onClose={() => setSelectedId(null)} />}
        </div>
    )
}
