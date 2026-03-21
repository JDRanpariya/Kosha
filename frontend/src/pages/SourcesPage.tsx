// frontend/src/pages/SourcesPage.tsx

import { useState } from 'react'
import { Plus, Trash2, RefreshCw, Check, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  useSources,
  useCreateSource,
  useDeleteSource,
  useTriggerIngestion,
  useUpdateSource,
} from '@/hooks/useSources'
import { formatDate } from '@/lib/utils'
import type { Source } from '@/types'

// ── Static metadata ───────────────────────────────────────────────────────────

const SOURCE_TYPES = [
  { value: 'rss',        label: 'RSS Feed',                   category: 'newsletters', placeholder: 'Feed URL (https://example.com/feed.rss)' },
  { value: 'substack',   label: 'Substack',                   category: 'newsletters', placeholder: 'Publication URL (https://name.substack.com)' },
  { value: 'email_imap', label: 'Newsletter via Email (IMAP)', category: 'newsletters', placeholder: 'IMAP host (imap.gmail.com)' },
  { value: 'arxiv',      label: 'arXiv',                      category: 'papers',      placeholder: 'Categories (cs.AI,stat.ML)' },
  { value: 'hackernews', label: 'Hacker News',                category: 'social',      placeholder: 'Tags — leave blank for front_page' },
  { value: 'reddit',     label: 'Reddit',                     category: 'social',      placeholder: 'Subreddits (MachineLearning,LocalLLaMA)' },
  { value: 'github',     label: 'GitHub Releases & Trending', category: 'social',      placeholder: 'Repos (openai/whisper,ollama/ollama) — leave blank for trending' },
  { value: 'spotify',    label: 'Spotify Podcast',            category: 'podcasts',    placeholder: 'Show ID' },
  { value: 'youtube',    label: 'YouTube Channel',            category: 'videos',      placeholder: 'Channel IDs (UCxxx,UCyyy)' },
] as const

type SourceTypeValue = (typeof SOURCE_TYPES)[number]['value']

const CATEGORY_COLOURS: Record<string, string> = {
  newsletters: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  papers:      'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  social:      'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  podcasts:    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  videos:      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  other:       'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
}

// ── Config builder ────────────────────────────────────────────────────────────

function buildConfigJson(type: string, value: string): Record<string, unknown> {
  const trimmed = value.trim()
  switch (type) {
    case 'rss':
      return { feed_url: trimmed }
    case 'substack':
      return { publication_url: trimmed }
    case 'arxiv':
      return { categories: trimmed.split(',').map((s) => s.trim()).filter(Boolean) }
    case 'hackernews':
      return { tags: trimmed || 'front_page' }
    case 'reddit':
      return { subreddits: trimmed.split(',').map((s) => s.trim()).filter(Boolean) }
    case 'github':
      return {
        repos: trimmed ? trimmed.split(',').map((s) => s.trim()).filter(Boolean) : [],
        fetch_trending: true,
      }
    case 'spotify':
      return { show_id: trimmed }
    case 'youtube':
      return { channels: trimmed.split(',').map((s) => s.trim()).filter(Boolean) }
    case 'email_imap':
      return { imap_host: trimmed }
    default:
      return {}
  }
}

// ── Helper: group sources by category ────────────────────────────────────────

function groupByCategory(sources: Source[]): Record<string, Source[]> {
  return sources.reduce<Record<string, Source[]>>((acc, src) => {
    const cat =
      SOURCE_TYPES.find((t) => t.value === src.type)?.category ?? 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(src)
    return acc
  }, {})
}

// ── Add-source form ───────────────────────────────────────────────────────────

interface AddSourceFormProps {
  onClose: () => void
}

function AddSourceForm({ onClose }: AddSourceFormProps) {
  const createSource = useCreateSource()
  const [formData, setFormData] = useState<{
    name: string
    type: string
    config: string
  }>({ name: '', type: 'rss', config: '' })

  const selectedMeta = SOURCE_TYPES.find((t) => t.value === formData.type)
  const needsConfig = formData.type !== 'hackernews'

  // Group types by category for <optgroup>
  const grouped = SOURCE_TYPES.reduce<Record<string, typeof SOURCE_TYPES[number][]>>(
    (acc, t) => {
      if (!acc[t.category]) acc[t.category] = []
      acc[t.category].push(t)
      return acc
    },
    {}
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const config_json = buildConfigJson(formData.type, formData.config)

    createSource.mutate(
      {
        name: formData.name,
        type: formData.type,
        url: formData.type === 'rss' ? formData.config : undefined,
        config_json,
      },
      {
        onSuccess: () => {
          onClose()
        },
      }
    )
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Add New Source</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="My Source"
              required
            />
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value, config: '' })
              }
            >
              {Object.entries(grouped).map(([cat, types]) => (
                <optgroup
                  key={cat}
                  label={cat.charAt(0).toUpperCase() + cat.slice(1)}
                >
                  {types.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* Configuration value */}
          {needsConfig && selectedMeta && (
            <div>
              <label className="block text-sm font-medium mb-1">
                Configuration
              </label>
              <Input
                value={formData.config}
                onChange={(e) =>
                  setFormData({ ...formData, config: e.target.value })
                }
                placeholder={selectedMeta.placeholder}
                required
              />
              {formData.type === 'email_imap' && (
                <p className="text-xs text-muted-foreground mt-1">
                  Enter the IMAP host. Username and password are read from
                  secrets files.
                </p>
              )}
              {formData.type === 'github' && (
                <p className="text-xs text-muted-foreground mt-1">
                  Leave blank to fetch trending only. API token is read from
                  secrets.
                </p>
              )}
              {formData.type === 'arxiv' && (
                <p className="text-xs text-muted-foreground mt-1">
                  Comma-separated category codes, e.g. cs.AI,stat.ML
                </p>
              )}
            </div>
          )}

          {createSource.isError && (
            <p className="text-sm text-destructive">
              {(createSource.error as Error).message ?? 'Failed to create source.'}
            </p>
          )}

          <div className="flex gap-2">
            <Button type="submit" disabled={createSource.isPending}>
              {createSource.isPending ? 'Adding…' : 'Add Source'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

// ── Source row ────────────────────────────────────────────────────────────────

interface SourceRowProps {
  source: Source
  category: string
}

function SourceRow({ source, category }: SourceRowProps) {
  const updateSource     = useUpdateSource()
  const deleteSource     = useDeleteSource()
  const triggerIngestion = useTriggerIngestion()

  const colourClass =
    CATEGORY_COLOURS[category] ?? CATEGORY_COLOURS.other

  const configPreview = source.url ?? JSON.stringify(source.config_json)

  return (
    <Card>
      <CardContent className="flex items-center justify-between p-4">
        {/* Left: info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold">{source.name}</h3>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${colourClass}`}
            >
              {source.type}
            </span>
            <Badge variant={source.enabled ? 'default' : 'secondary'}>
              {source.enabled ? 'Active' : 'Disabled'}
            </Badge>
          </div>

          <p className="text-sm text-muted-foreground mt-1 truncate max-w-md">
            {configPreview}
          </p>

          <p className="text-xs text-muted-foreground mt-0.5">
            Last fetched:{' '}
            {source.last_fetched_at
              ? formatDate(source.last_fetched_at)
              : 'Never'}
          </p>
        </div>

        {/* Right: actions */}
        <div className="flex items-center gap-1 ml-4 shrink-0">
          {/* Toggle enabled */}
          <Button
            variant="ghost"
            size="icon"
            title={source.enabled ? 'Disable source' : 'Enable source'}
            onClick={() =>
              updateSource.mutate({
                id: source.id,
                data: { enabled: !source.enabled },
              })
            }
            disabled={updateSource.isPending}
          >
            {source.enabled ? (
              <Check className="h-4 w-4 text-green-600" />
            ) : (
              <X className="h-4 w-4 text-muted-foreground" />
            )}
          </Button>

          {/* Fetch now */}
          <Button
            variant="ghost"
            size="icon"
            title="Fetch now"
            onClick={() => triggerIngestion.mutate(source.id)}
            disabled={triggerIngestion.isPending}
          >
            <RefreshCw
              className={`h-4 w-4 ${
                triggerIngestion.isPending ? 'animate-spin' : ''
              }`}
            />
          </Button>

          {/* Delete */}
          <Button
            variant="ghost"
            size="icon"
            title="Delete source"
            onClick={() => {
              if (confirm(`Delete "${source.name}"?`)) {
                deleteSource.mutate(source.id)
              }
            }}
            disabled={deleteSource.isPending}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function SourcesPage() {
  const { data: sources = [], isLoading, isError } = useSources()
  const [showForm, setShowForm] = useState(false)

  const grouped = groupByCategory(sources)

  // Preserve a stable category order
  const categoryOrder = ['newsletters', 'papers', 'social', 'podcasts', 'videos', 'other']
  const sortedCategories = [
    ...categoryOrder.filter((c) => grouped[c]),
    ...Object.keys(grouped).filter((c) => !categoryOrder.includes(c)),
  ]

  return (
    <div>
      {/* ── Page header ── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Content Sources</h1>
          <p className="text-muted-foreground">
            Manage RSS feeds, newsletters, social feeds, podcasts, and channels
          </p>
        </div>
        <Button onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Source
        </Button>
      </div>

      {/* ── Add form ── */}
      {showForm && <AddSourceForm onClose={() => setShowForm(false)} />}

      {/* ── States ── */}
      {isLoading && <p className="text-muted-foreground">Loading sources…</p>}

      {isError && (
        <p className="text-destructive">
          Failed to load sources. Is the backend running?
        </p>
      )}

      {/* ── Source list ── */}
      {!isLoading && !isError && (
        <div className="space-y-8">
          {sortedCategories.map((category) => (
            <div key={category}>
              <h2 className="text-lg font-semibold capitalize mb-3">
                {category}
              </h2>
              <div className="space-y-3">
                {grouped[category].map((source) => (
                  <SourceRow
                    key={source.id}
                    source={source}
                    category={category}
                  />
                ))}
              </div>
            </div>
          ))}

          {sources.length === 0 && (
            <div className="text-center py-16 text-muted-foreground">
              <p className="text-lg">No sources configured yet.</p>
              <p className="text-sm mt-1">
                Click{' '}
                <button
                  className="underline hover:text-foreground transition-colors"
                  onClick={() => setShowForm(true)}
                >
                  Add Source
                </button>{' '}
                to get started.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
