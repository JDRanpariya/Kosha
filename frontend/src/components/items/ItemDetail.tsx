import { X, ExternalLink, Bookmark } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { useItemDetail, useFeedback } from '@/hooks/useItems'

function SkeletonBlock({ w }: { w: string }) {
    return <div className="skeleton-warm rounded" style={{ width: w, height: '14px' }} />
}

interface ItemDetailProps {
    itemId: number
    isSaved: boolean
    onClose: () => void
}

export function ItemDetail({ itemId, isSaved, onClose }: ItemDetailProps) {
    const { data: item, isLoading } = useItemDetail(itemId)
    const feedback = useFeedback()

    const handleSave = () => {
        if (!item) return
        feedback.mutate({ item_id: item.id, type: isSaved ? 'unsave' : 'saved' })
    }

    const sourceType = item?.metadata?.source_type as string | undefined

    return (
        <div className="flex flex-col h-full border-l border-border bg-background overflow-hidden">

            <div className="flex items-center justify-between px-5 py-2.5 border-b border-border shrink-0">
                <div className="flex items-center gap-1.5">
                    {item && (
                        <>
                            <button
                                onClick={handleSave}
                                className={cn(
                                    'flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[12px] transition-colors',
                                    isSaved
                                        ? 'bg-sage-light text-sage-dark font-medium'
                                        : 'text-ink-mid hover:bg-parchment-deep hover:text-ink',
                                )}
                            >
                                <Bookmark className={cn('h-3 w-3', isSaved && 'fill-current')} />
                                {isSaved ? 'Remove from list' : 'Save to list'}
                            </button>
                            <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[12px] text-ink-mid hover:bg-parchment-deep hover:text-ink transition-colors"
                            >
                                <ExternalLink className="h-3 w-3" />
                                Open original
                            </a>
                        </>
                    )}
                </div>
                <button onClick={onClose} aria-label="Close"
                    className="p-1.5 rounded text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors">
                    <X className="h-3.5 w-3.5" />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                    <div className="px-7 py-8 space-y-3">
                        <SkeletonBlock w="55%" />
                        <SkeletonBlock w="80%" />
                        <SkeletonBlock w="68%" />
                        <div className="pt-5 space-y-2.5">
                            {[100, 94, 88, 96, 82].map((w, i) => (
                                <SkeletonBlock key={i} w={`${w}%`} />
                            ))}
                        </div>
                    </div>
                ) : item ? (
                    <article className="px-7 py-8">
                        <div className="flex items-center gap-2 text-[10px] text-ink-faint uppercase tracking-[0.1em] mb-4">
                            {sourceType && <span>{sourceType.replace(/_/g, ' ')}</span>}
                            {sourceType && <span>·</span>}
                            <span>{formatDate(item.published_at)}</span>
                        </div>
                        <h1 className="font-serif text-[22px] font-normal leading-snug text-ink mb-3 tracking-tight">
                            {item.title}
                        </h1>
                        {item.author && (
                            <p className="text-[12px] text-ink-mid mb-7 pb-7 border-b border-border">{item.author}</p>
                        )}
                        {item.content ? (
                            <div className="prose-reading space-y-0">
                                {item.content.split('\n').filter(p => p.trim()).map((para, i) => (
                                    <p key={i} className="mb-[1.4em] last:mb-0 text-[15px] leading-[1.85]">{para}</p>
                                ))}
                            </div>
                        ) : (
                            <div className="py-12 text-center space-y-2">
                                <p className="text-[13px] text-ink-faint">Full content not stored.</p>
                                <a href={item.url} target="_blank" rel="noopener noreferrer"
                                    className="text-[13px] text-sage hover:underline underline-offset-4">
                                    Read at source →
                                </a>
                            </div>
                        )}
                    </article>
                ) : null}
            </div>
        </div>
    )
}
