import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { digestApi, feedbackApi } from '@/lib/api'
import type { FeedbackType } from '@/types'

export function useDailyDigest() {
  return useQuery({
    queryKey: ['digest', 'daily'],
    queryFn: digestApi.getDaily,
  })
}

export function useItemDetail(id: number | null) {
  return useQuery({
    queryKey: ['item', id],
    queryFn: () => (id ? digestApi.getItem(id) : null),
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
