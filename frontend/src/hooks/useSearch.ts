import { useQuery } from '@tanstack/react-query'
import { searchApi } from '@/lib/api'

export function useSearch(query: string, enabled = true) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => searchApi.search(query),
    enabled: enabled && query.length >= 2,
    staleTime: 1000 * 60 * 2, // 2 minutes
  })
}
