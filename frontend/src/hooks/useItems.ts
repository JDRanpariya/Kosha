import {
  useInfiniteQuery,
  useQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'
import { digestApi, feedbackApi } from '@/lib/api'
import type { FeedbackType, TeachSignal } from '@/types'

const PAGE_SIZE = 20

// ── Digest ────────────────────────────────────────────────────────────────

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

/** Lightweight hook just for the sidebar badge count */
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

// ── Item detail ───────────────────────────────────────────────────────────

export function useItemDetail(id: number | null) {
  return useQuery({
    queryKey: ['item', id],
    queryFn: () => digestApi.getItem(id!),
    enabled: !!id,
  })
}

// ── Saved / reading list ──────────────────────────────────────────────────

export function useSavedItems() {
  return useQuery({
    queryKey: ['saved'],
    queryFn: feedbackApi.getSaved,
  })
}

// ── Feedback (save / skip) ────────────────────────────────────────────────

export function useFeedback() {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (feedback: FeedbackType) => feedbackApi.submit(feedback),
    onSuccess: (_, vars) => {
      if (vars.type === 'saved') {
        qc.invalidateQueries({ queryKey: ['saved'] })
      }
      // Optimistically remove dismissed items from digest view
      if (vars.type === 'dismissed') {
        qc.invalidateQueries({ queryKey: ['digest'] })
      }
    },
  })
}

// ── Teach signal ──────────────────────────────────────────────────────────
// Records *why* the user found an item interesting.
// This is the seed data for Phase 2 preference learning.

export function useTeachSignal() {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (signal: TeachSignal) => feedbackApi.submitTeach(signal),
    onSuccess: () => {
      // Nothing to invalidate — teach signals are write-only from the UI
      // The backend accumulates them for the intelligence layer
    },
  })
}
