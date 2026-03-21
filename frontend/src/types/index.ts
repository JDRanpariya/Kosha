// ── Source ────────────────────────────────────────────────────────────────

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
  | 'github'
  | 'spotify'
  | 'youtube'
  | 'youtube_subscriptions'

export interface SourceCreate {
  name: string
  type: string
  url?: string
  config_json?: Record<string, unknown>
}

// ── Item ──────────────────────────────────────────────────────────────────

export interface Item {
  id: number
  title: string
  author: string | null
  url: string
  published_at: string | null
  source_id: number
  source_type?: string   // populated by backend join
  preview?: string
  // NOTE: similarity is intentionally absent from Phase 1 Item.
  // It will be added back in Phase 2 as `resonance?: number`
  // and only shown when value >= 0.7.
}

export interface ItemDetail extends Item {
  content: string | null
  metadata: Record<string, unknown>
}

// ── Digest ────────────────────────────────────────────────────────────────

export interface DigestResponse {
  date: string
  total: number
  limit: number
  offset: number
  items: Item[]
}

// ── Search ────────────────────────────────────────────────────────────────

export interface SearchResponse {
  query: string
  count: number
  items: Item[]
}

// ── Saved ─────────────────────────────────────────────────────────────────

export interface SavedResponse {
  count: number
  item_ids: number[]
  items: Item[]
}

// ── Feedback ──────────────────────────────────────────────────────────────

export interface FeedbackType {
  item_id: number
  type: 'viewed' | 'saved' | 'dismissed'
  user_id?: number
}

// ── Teach signal ──────────────────────────────────────────────────────────
// The core data structure for Phase 2 preference learning.
// Records not just *that* you liked something, but *why*.

export interface TeachSignal {
  item_id: number
  // Which tag(s) the user selected as their reason for interest.
  // Tags are generated from item content by the backend.
  selected_tags: string[]
  // Optional free-text elaboration (Phase 2+)
  note?: string
}

// ── Connector meta ────────────────────────────────────────────────────────

export interface ConnectorMeta {
  category: string
  type: string
  display_name: string
  required_fields: string[]
  optional_fields: string[]
  example_config: Record<string, unknown>
}
