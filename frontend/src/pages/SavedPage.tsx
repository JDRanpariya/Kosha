import { useState } from 'react'
import { useSavedItems } from '@/hooks/useItems'
import { ItemList } from '@/components/items/ItemList'
import { ItemDetail } from '@/components/items/ItemDetail'

export function SavedPage() {
    const [selectedId, setSelectedId] = useState<number | null>(null)
    const { data: saved, isLoading } = useSavedItems()

    return (
        <>
            <div className="mb-8 fade-up">
                <p className="text-xs uppercase tracking-[0.15em] text-ink-faint font-medium mb-1">
                    Your collection
                </p>
                <h1 className="font-serif text-3xl font-normal text-ink">
                    Saved
                </h1>
            </div>

            {!isLoading && saved && saved.count > 0 && (
                <div className="section-divider" style={{ opacity: 1 }}>
                    {saved.count} items saved
                </div>
            )}

            <ItemList
                items={saved?.items ?? []}
                savedIds={saved?.item_ids ?? []}
                isLoading={isLoading}
                onSelectItem={setSelectedId}
            />

            {selectedId && (
                <ItemDetail
                    itemId={selectedId}
                    isSaved={savedIds.has(selectedId)}   // ← ADD
                    onClose={() => setSelectedId(null)}
                />
            )}
        </>
    )
}
