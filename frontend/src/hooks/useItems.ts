import {
    useInfiniteQuery,
    useQuery,
    useMutation,
    useQueryClient,
} from '@tanstack/react-query'
import { digestApi, feedbackApi } from '@/lib/api'
import type { FeedbackType, DigestResponse } from '@/types'

const PAGE_SIZE = 20

export function useDailyDigest() {
    return useInfiniteQuery({
        queryKey: ['digest', 'daily'],
        queryFn: ({ pageParam }) => digestApi.getDaily(PAGE_SIZE, pageParam as number),
        initialPageParam: 0,
        getNextPageParam: (lastPage, allPages) => {
            const fetched = allPages.reduce((s, p) => s + p.items.length, 0)
            return fetched < lastPage.total ? fetched : undefined
        },
    })
}

export function useDailyDigestCount() {
    const digest = useQuery({
        queryKey: ['digest', 'daily', 'count'],
        queryFn: () => digestApi.getDaily(1, 0),
        staleTime: 1000 * 60 * 5,
    })
    const saved = useQuery({
        queryKey: ['saved'],
        queryFn: feedbackApi.getSaved,
        staleTime: 1000 * 60 * 5,
    })
    return {
        digestCount: digest.data?.total ?? 0,
        savedCount: saved.data?.count ?? 0,
    }
}

export function useItemDetail(id: number | null) {
    return useQuery({
        queryKey: ['item', id],
        queryFn: () => digestApi.getItem(id!),
        enabled: !!id,
    })
}

export function useSavedItems() {
    return useQuery({
        queryKey: ['saved'],
        queryFn: feedbackApi.getSaved,
    })
}

export function useFeedback(onDismiss?: (itemId: number) => void) {
    const qc = useQueryClient()

    return useMutation({
        mutationFn: (feedback: FeedbackType) => feedbackApi.submit(feedback),

        onMutate: async (vars) => {
            if (vars.type === 'dismissed') {
                await qc.cancelQueries({ queryKey: ['digest', 'daily'] })
                const previous = qc.getQueryData(['digest', 'daily'])
                qc.setQueryData<{ pages: DigestResponse[]; pageParams: number[] }>(
                    ['digest', 'daily'],
                    (old) => {
                        if (!old) return old
                        return {
                            ...old,
                            pages: old.pages.map((page) => ({
                                ...page,
                                total: page.total - 1,
                                items: page.items.filter((it) => it.id !== vars.item_id),
                            })),
                        }
                    },
                )
                onDismiss?.(vars.item_id)
                return { previous }
            }

            if (vars.type === 'unsave') {
                await qc.cancelQueries({ queryKey: ['saved'] })
                const previous = qc.getQueryData(['saved'])
                qc.setQueryData<{ count: number; item_ids: number[]; items: unknown[] }>(
                    ['saved'],
                    (old) => {
                        if (!old) return old
                        return {
                            count: old.count - 1,
                            item_ids: old.item_ids.filter((id) => id !== vars.item_id),
                            items: old.items.filter((it: any) => it.id !== vars.item_id),
                        }
                    },
                )
                return { previous }
            }
        },

        onError: (_err, vars, context: any) => {
            if (vars.type === 'dismissed' && context?.previous)
                qc.setQueryData(['digest', 'daily'], context.previous)
            if (vars.type === 'unsave' && context?.previous)
                qc.setQueryData(['saved'], context.previous)
        },

        onSuccess: (_data, vars) => {
            if (vars.type === 'saved') qc.invalidateQueries({ queryKey: ['saved'] })
            if (vars.type === 'dismissed') qc.invalidateQueries({ queryKey: ['digest', 'daily'] })
            if (vars.type === 'unsave') qc.invalidateQueries({ queryKey: ['saved'] })
        },
    })
}
