import { useState } from 'react'
import { useDailyDigest, useSavedItems } from '@/hooks/useItems'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'
import { Button } from '@/components/ui/button'

export function DigestPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const {
    data,
    isLoading,
    isFetchingNextPage,
    fetchNextPage,
    hasNextPage,
  } = useDailyDigest()

  const { data: saved } = useSavedItems()

  const items = data?.pages.flatMap((p) => p.items) ?? []
  const total = data?.pages[0]?.total ?? 0

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Daily Digest</h1>
        <p className="text-muted-foreground">
          {data ? `${total} items from the last 24 hours` : 'Loading...'}
        </p>
      </div>

      <ItemList
        items={items}
        savedIds={saved?.item_ids ?? []}
        isLoading={isLoading}
        onSelectItem={setSelectedId}
      />

      {hasNextPage && (
        <div className="mt-6 flex justify-center">
          <Button
            variant="outline"
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
          >
            {isFetchingNextPage ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}

      {selectedId && (
        <ItemDetail itemId={selectedId} onClose={() => setSelectedId(null)} />
      )}
    </div>
  )
}
