import { X, ExternalLink, Bookmark } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDate } from '@/lib/utils'
import { useItemDetail, useFeedback } from '@/hooks/useItems'

interface ItemDetailProps {
  itemId: number
  onClose: () => void
}

export function ItemDetail({ itemId, onClose }: ItemDetailProps) {
  const { data: item, isLoading } = useItemDetail(itemId)
  const feedback = useFeedback()

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm">
        <div className="fixed right-0 top-0 h-full w-full max-w-2xl bg-background border-l shadow-lg p-6">
          <Skeleton className="h-8 w-3/4 mb-4" />
          <Skeleton className="h-4 w-1/4 mb-8" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  if (!item) return null

  return (
    <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" onClick={onClose}>
      <div
        className="fixed right-0 top-0 h-full w-full max-w-2xl bg-background border-l shadow-lg overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-background border-b p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => feedback.mutate({ item_id: item.id, type: 'saved' })}
            >
              <Bookmark className="h-4 w-4 mr-1" />
              Save
            </Button>
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              <Button variant="ghost" size="sm">
                <ExternalLink className="h-4 w-4 mr-1" />
                Open
              </Button>
            </a>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <article className="p-6">
          <h1 className="text-2xl font-bold mb-2">{item.title}</h1>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
            {item.author && <span>{item.author}</span>}
            {item.author && item.published_at && <span>•</span>}
            <span>{formatDate(item.published_at)}</span>
          </div>

          {item.metadata && Object.keys(item.metadata).length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {item.metadata.source_type && (
                <Badge variant="outline">{String(item.metadata.source_type)}</Badge>
              )}
            </div>
          )}

          <div className="prose prose-sm dark:prose-invert max-w-none">
            {item.content ? (
              <div className="whitespace-pre-wrap">{item.content}</div>
            ) : (
              <p className="text-muted-foreground">No content available</p>
            )}
          </div>
        </article>
      </div>
    </div>
  )
}
