import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sourcesApi, ingestApi } from '@/lib/api'
import type { SourceCreate, Source } from '@/types'

export function useSources() {
  return useQuery({
    queryKey: ['sources'],
    queryFn: sourcesApi.list,
  })
}

export function useCreateSource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (source: SourceCreate) => sourcesApi.create(source),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })
}

export function useUpdateSource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Source> }) =>
      sourcesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })
}

export function useDeleteSource() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => sourcesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })
}

export function useTriggerIngestion() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (sourceId?: number) =>
      sourceId ? ingestApi.triggerSource(sourceId) : ingestApi.triggerAll(),
    onSuccess: () => {
      // Refetch digest after ingestion starts
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['digest'] })
      }, 5000)
    },
  })
}
