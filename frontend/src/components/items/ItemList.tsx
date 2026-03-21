import { ItemCard } from './ItemCard'
import { Skeleton } from '@/components/ui/skeleton'
import type { Item } from '@/types'

interface ItemListProps {
  items: Item[]
  savedIds?: number[]
  isLoading?: boolean
  onSelectItem?: (id: number) => void
}

export function ItemList({ items, savedIds = [], isLoading, onSelectItem }: ItemListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="rounded-lg border p-6">
            <Skeleton className="h-5 w-3/4 mb-2" />
            <Skeleton className="h-4 w-1/4 mb-4" />
            <Skeleton className="h-16 w-full" />
          </div>
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No items to display</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <ItemCard
          key={item.id}
          item={item}
          isSaved={savedIds.includes(item.id)}
          onSelect={onSelectItem}
        />
      ))}
    </div>
  )
}
