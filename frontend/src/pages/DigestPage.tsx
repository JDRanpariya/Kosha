import { useState } from 'react'
import { useDailyDigest, useSavedItems } from '@/hooks/useItems'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'

export function DigestPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const { data: digest, isLoading } = useDailyDigest()
  const { data: saved } = useSavedItems()

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Daily Digest</h1>
        <p className="text-muted-foreground">
          {digest ? `${digest.count} items from the last 24 hours` : 'Loading...'}
        </p>
      </div>

      <ItemList
        items={digest?.items ?? []}
        savedIds={saved?.item_ids ?? []}
        isLoading={isLoading}
        onSelectItem={setSelectedId}
      />

      {selectedId && <ItemDetail itemId={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  )
}
