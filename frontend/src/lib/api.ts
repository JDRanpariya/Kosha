import type {
    DigestResponse,
    ItemDetail,
    SearchResponse,
    Source,
    SourceCreate,
    FeedbackType,
    SavedResponse,
} from '@/types'

const BASE = '/api'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${url}`, {
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        ...options,
    })
    if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`)
    }
    return res.json()
}

export const digestApi = {
    getDaily: (limit = 20, offset = 0) =>
        fetchJson<DigestResponse>(`/digest/daily?limit=${limit}&offset=${offset}`),
    getItem: (id: number) =>
        fetchJson<{ item: ItemDetail }>(`/digest/item/${id}`).then(r => r.item),
}

export const searchApi = {
    search: (query: string, limit = 20) =>
        fetchJson<SearchResponse>(`/search/?q=${encodeURIComponent(query)}&limit=${limit}`),
}

export const sourcesApi = {
    list: () =>
        fetchJson<{ sources: Source[]; count: number }>('/sources/').then(r => r.sources),
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
        fetchJson<{ status: string }>(`/sources/${id}`, { method: 'DELETE' }),
}

export const feedbackApi = {
    submit: (feedback: FeedbackType) =>
        fetchJson<{ status: string; type: string; item_id: number }>('/feedback/', {
            method: 'POST',
            body: JSON.stringify(feedback),
        }),
    getSaved: () => fetchJson<SavedResponse>('/feedback/saved'),
}

export const ingestApi = {
    triggerSource: (sourceId: number) =>
        fetchJson<{ status: string }>(`/ingest/trigger/${sourceId}`, { method: 'POST' }),
    triggerAll: () =>
        fetchJson<{ status: string }>('/ingest/trigger-all', { method: 'POST' }),
}
