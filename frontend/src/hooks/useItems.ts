import { useInfiniteQuery, useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { digestApi, feedbackApi } from '@/lib/api'
import type { FeedbackType } from '@/types'

const DIGEST_PAGE_SIZE = 20

export function useDailyDigest() {
  return useInfiniteQuery({
    queryKey: ['digest', 'daily'],
    queryFn: ({ pageParam }) => digestApi.getDaily(DIGEST_PAGE_SIZE, pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const fetched = allPages.reduce((sum, p) => sum + p.items.length, 0)
      return fetched < lastPage.total ? fetched : undefined
    },
  })
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

export function useFeedback() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (feedback: FeedbackType) => feedbackApi.submit(feedback),
    onSuccess: (_, variables) => {
      if (variables.type === 'saved') {
        queryClient.invalidateQueries({ queryKey: ['saved'] })
      }
    },
  })
}
