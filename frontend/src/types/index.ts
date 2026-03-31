// ── Source ──

export interface Source {
  id: number
  name: string
  type: SourceType
  url: string | null
  enabled: boolean
  last_fetched_at: string | null
  config_json: Record<string, unknown>
}

export type SourceType =
  | 'rss'
  | 'substack'
  | 'email_imap'
  | 'arxiv'
  | 'hackernews'
  | 'reddit'
  | 'youtube'

export interface SourceCreate {
  name: string
  type: string
  url?: string
  config_json?: Record<string, unknown>
}

// ── Item ──

export interface Item {
  id: number
  title: string
  author: string | null
  url: string
  published_at: string | null
  source_id: number
  source_type?: string
  preview?: string
}

export interface ItemDetail extends Item {
  content: string | null
  metadata: Record<string, unknown>
}

// ── Digest ──

export interface DigestResponse {
  date: string
  total: number
  limit: number
  offset: number
  items: Item[]
}

// ── Search ──

export interface SearchResponse {
  query: string
  count: number
  items: Item[]
}

// ── Saved ──

export interface SavedResponse {
  count: number
  item_ids: number[]
  items: Item[]
}

// ── Feedback ──

export interface FeedbackType {
  item_id: number
  type: 'viewed' | 'saved' | 'unsave' | 'dismissed'
}
