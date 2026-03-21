export interface Source {
  id: number
  name: string
  type:
    | 'rss'
    | 'substack'
    | 'email_imap'
    | 'arxiv'
    | 'hackernews'
    | 'reddit'
    | 'github'
    | 'spotify'
    | 'youtube'
  url: string | null
  enabled: boolean
  last_fetched_at: string | null
  config_json: Record<string, unknown>
}

export interface Item {
  id: number
  title: string
  author: string | null
  url: string
  published_at: string | null
  source_id: number
  preview?: string
  similarity?: number
}

export interface ItemDetail extends Item {
  content: string | null
  metadata: Record<string, unknown>
}

export interface DigestResponse {
  date: string
  total: number
  limit: number
  offset: number
  items: Item[]
}

export interface SearchResponse {
  query: string
  count: number
  items: Item[]
}

export interface SavedResponse {
  count: number
  item_ids: number[]
  items: Item[]
}

export interface FeedbackType {
  item_id: number
  type: 'viewed' | 'saved' | 'dismissed'
  user_id?: number
}

export interface SourceCreate {
  name: string
  type: string
  url?: string
  config_json?: Record<string, unknown>
}

export interface ConnectorMeta {
  category: string
  type: string
  display_name: string
  required_fields: string[]
  optional_fields: string[]
  example_config: Record<string, unknown>
}
