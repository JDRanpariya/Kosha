import { useState } from 'react'
import { useSavedItems, useDailyDigest } from '@/hooks/useItems'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'

export function SavedPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const { data: saved, isLoading: savedLoading } = useSavedItems()
  const { data: digest } = useDailyDigest()

  // Filter digest items to only show saved ones
  const savedItems = digest?.items.filter((item) => saved?.item_ids.includes(item.id)) ?? []

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Saved Items</h1>
        <p className="text-muted-foreground">
          {saved ? `${saved.count} saved items` : 'Loading...'}
        </p>
      </div>

      <ItemList
        items={savedItems}
        savedIds={saved?.item_ids ?? []}
        isLoading={savedLoading}
        onSelectItem={setSelectedId}
      />

      {selectedId && <ItemDetail itemId={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  )
}
