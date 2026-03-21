import { Bookmark, ExternalLink, X } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatRelativeTime, truncate } from '@/lib/utils'
import { useFeedback } from '@/hooks/useItems'
import type { Item } from '@/types'

interface ItemCardProps {
    item: Item
    onSelect?: (id: number) => void
    isSaved?: boolean
}

export function ItemCard({ item, onSelect, isSaved = false }: ItemCardProps) {
    const feedback = useFeedback()

    const handleSave = (e: React.MouseEvent) => {
        e.stopPropagation()
        feedback.mutate({ item_id: item.id, type: 'saved' })
    }

    const handleDismiss = (e: React.MouseEvent) => {
        e.stopPropagation()
        feedback.mutate({ item_id: item.id, type: 'dismissed' })
    }

    return (
        <Card
            className="cursor-pointer transition-shadow hover:shadow-md"
            onClick={() => onSelect?.(item.id)}
        >
            <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                        <h3 className="font-semibold leading-tight line-clamp-2">{item.title}</h3>
                        <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
                            {item.author && <span>{item.author}</span>}
                            {item.author && item.published_at && <span>•</span>}
                            <span>{formatRelativeTime(item.published_at)}</span>
                        </div>
                    </div>
                    {item.similarity && (
                        <Badge variant="secondary" className="shrink-0">
                            {Math.round(item.similarity * 100)}%
                        </Badge>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                {item.preview && (
                    <p className="text-sm text-muted-foreground line-clamp-3">
                        {truncate(item.preview, 200)}
                    </p>
                )}
                <div className="flex items-center gap-2 mt-4">
                    <Button
                        variant={isSaved ? 'default' : 'ghost'}
                        size="sm"
                        onClick={handleSave}
                        disabled={feedback.isPending}
                    >
                        <Bookmark className={`h-4 w-4 mr-1 ${isSaved ? 'fill-current' : ''}`} />
                        {isSaved ? 'Saved' : 'Save'}
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleDismiss} disabled={feedback.isPending}>
                        <X className="h-4 w-4 mr-1" />
                        Dismiss
                    </Button>
                    <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="ml-auto"
                    >
                        <Button variant="ghost" size="sm">
                            <ExternalLink className="h-4 w-4" />
                        </Button>
                    </a>
                </div>
            </CardContent>
        </Card>
    )
}
