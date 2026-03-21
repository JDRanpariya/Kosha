import type {
  DigestResponse,
  ItemDetail,
  SearchResponse,
  Source,
  SourceCreate,
  FeedbackType,
} from '@/types'

const API_BASE = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Digest endpoints
export const digestApi = {
  getDaily: () => fetchJson<DigestResponse>('/digest/daily'),
  getItem: (id: number) => fetchJson<ItemDetail>(`/digest/item/${id}`),
}

// Search endpoints
export const searchApi = {
  search: (query: string, limit = 20) =>
    fetchJson<SearchResponse>(`/search/?q=${encodeURIComponent(query)}&limit=${limit}`),
}

// Sources endpoints
export const sourcesApi = {
  list: () => fetchJson<Source[]>('/sources/'),
  create: (source: SourceCreate) =>
    fetchJson<{ id: number; name: string }>('/sources/', {
      method: 'POST',
      body: JSON.stringify(source),
    }),
  update: (id: number, data: Partial<Source>) =>
    fetchJson<{ status: string }>(`/sources/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchJson<{ status: string }>(`/sources/${id}`, {
      method: 'DELETE',
    }),
}

// Feedback endpoints
export const feedbackApi = {
  submit: (feedback: FeedbackType) =>
    fetchJson<{ status: string; type: string; item_id: number }>('/feedback/', {
      method: 'POST',
      body: JSON.stringify(feedback),
    }),
  getSaved: () =>
    fetchJson<{ count: number; item_ids: number[] }>('/feedback/saved'),
}

// Ingest endpoints
export const ingestApi = {
  triggerSource: (sourceId: number) =>
    fetchJson<{ status: string; source_id: number }>(`/ingest/trigger/${sourceId}`, {
      method: 'POST',
    }),
  triggerAll: () =>
    fetchJson<{ status: string }>('/ingest/trigger-all', {
      method: 'POST',
    }),
}
