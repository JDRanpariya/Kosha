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

const SOURCE_TYPES = [
  // Newsletters
  { value: 'rss',        label: 'RSS Feed',                  category: 'newsletters', placeholder: 'Feed URL (https://example.com/feed.rss)' },
  { value: 'substack',   label: 'Substack',                  category: 'newsletters', placeholder: 'Publication URL (https://name.substack.com)' },
  { value: 'email_imap', label: 'Newsletter via Email (IMAP)', category: 'newsletters', placeholder: 'imap.gmail.com' },
  // Papers
  { value: 'arxiv',      label: 'arXiv',                     category: 'papers',      placeholder: 'Categories (cs.AI,stat.ML)' },
  // Social
  { value: 'hackernews', label: 'Hacker News',               category: 'social',      placeholder: 'Optional: tags (front_page, ask_hn…)' },
  { value: 'reddit',     label: 'Reddit',                    category: 'social',      placeholder: 'Subreddits (MachineLearning,LocalLLaMA)' },
  { value: 'github',     label: 'GitHub Releases & Trending', category: 'social',     placeholder: 'Repos (openai/whisper,ollama/ollama)' },
  // Podcasts
  { value: 'spotify',    label: 'Spotify Podcast',           category: 'podcasts',    placeholder: 'Show ID' },
  // Videos
  { value: 'youtube',    label: 'YouTube Channel',           category: 'videos',      placeholder: 'Channel IDs (UCxxx,UCyyy)' },
]

const CATEGORY_COLOURS: Record<string, string> = {
  newsletters: 'bg-blue-100 text-blue-800',
  papers:      'bg-purple-100 text-purple-800',
  social:      'bg-orange-100 text-orange-800',
  podcasts:    'bg-green-100 text-green-800',
  videos:      'bg-red-100 text-red-800',
}

function buildConfigJson(type: string, value: string): Record<string, unknown> {
  switch (type) {
    case 'rss':
      return { feed_url: value }
    case 'substack':
      return { publication_url: value }
    case 'arxiv':
      return { categories: value.split(',').map((s) => s.trim()) }
    case 'hackernews':
      return value ? { tags: value } : { tags: 'front_page' }
    case 'reddit':
      return { subreddits: value.split(',').map((s) => s.trim()) }
    case 'github':
      return {
        repos: value ? value.split(',').map((s) => s.trim()) : [],
        fetch_trending: true,
      }
    case 'spotify':
      return { show_id: value }
    case 'youtube':
      return { channels: value.split(',').map((s) => s.trim()) }
    case 'email_imap':
      // For IMAP the main "config" field is the host; other fields need
      // the user to edit config_json directly for now.
      return { imap_host: value }
    default:
      return {}
  }
}

export function SourcesPage() {
  const { data: sources, isLoading } = useSources()
  const createSource  = useCreateSource()
  const deleteSource  = useDeleteSource()
  const updateSource  = useUpdateSource()
  const triggerIngestion = useTriggerIngestion()

  const [showForm, setShowForm]   = useState(false)
  const [formData, setFormData]   = useState({ name: '', type: 'rss', config: '' })

  const selectedMeta = SOURCE_TYPES.find((t) => t.value === formData.type)

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
          setFormData({ name: '', type: 'rss', config: '' })
          setShowForm(false)
        },
      }
    )
  }

  // Group sources by category for display
  const grouped = (sources ?? []).reduce<Record<string, typeof sources>>((acc, src) => {
    const cat = SOURCE_TYPES.find((t) => t.value === src!.type)?.category ?? 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat]!.push(src)
    return acc
  }, {})

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Content Sources</h1>
          <p className="text-muted-foreground">
            Manage RSS feeds, newsletters, social feeds, podcasts, and channels
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Source
        </Button>
      </div>

      {/* Add source form */}
      {showForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Add New Source</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="My Source"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Type</label>
                <select
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value, config: '' })}
                >
                  {Object.entries(
                    SOURCE_TYPES.reduce<Record<string, typeof SOURCE_TYPES>>((acc, t) => {
                      if (!acc[t.category]) acc[t.category] = []
                      acc[t.category].push(t)
                      return acc
                    }, {})
                  ).map(([cat, types]) => (
                    <optgroup key={cat} label={cat.charAt(0).toUpperCase() + cat.slice(1)}>
                      {types.map((t) => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>

              {/* Only show config field for types that need one */}
              {selectedMeta && formData.type !== 'hackernews' && (
                <div>
                  <label className="text-sm font-medium">Configuration</label>
                  <Input
                    value={formData.config}
                    onChange={(e) => setFormData({ ...formData, config: e.target.value })}
                    placeholder={selectedMeta.placeholder}
                    required={formData.type !== 'hackernews'}
                  />
                  {formData.type === 'email_imap' && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Enter the IMAP host. Username and password are read from secrets files.
                    </p>
                  )}
                  {formData.type === 'github' && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Leave blank to fetch trending only. API token is read from secrets.
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <Button type="submit" disabled={createSource.isPending}>
                  {createSource.isPending ? 'Adding…' : 'Add Source'}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Sources list grouped by category */}
      {isLoading ? (
        <p>Loading sources…</p>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([category, categorySources]) => (
            <div key={category}>
              <h2 className="text-lg font-semibold capitalize mb-3">{category}</h2>
              <div className="space-y-3">
                {categorySources?.map((source) => source && (
                  <Card key={source.id}>
                    <CardContent className="flex items-center justify-between p-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold">{source.name}</h3>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                              CATEGORY_COLOURS[category] ?? 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {source.type}
                          </span>
                          <Badge variant={source.enabled ? 'default' : 'secondary'}>
                            {source.enabled ? 'Active' : 'Disabled'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1 truncate">
                          {source.url ?? JSON.stringify(source.config)}
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          Last fetched:{' '}
                          {source.last_fetched_at
                            ? formatDate(source.last_fetched_at)
                            : 'Never'}
                        </p>
                      </div>

                      <div className="flex items-center gap-1 ml-4 shrink-0">
                        <Button
                          variant="ghost"
                          size="icon"
                          title={source.enabled ? 'Disable' : 'Enable'}
                          onClick={() =>
                            updateSource.mutate({
                              id: source.id,
                              data: { enabled: !source.enabled },
                            })
                          }
                        >
                          {source.enabled ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <X className="h-4 w-4" />
                          )}
                        </Button>
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
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete source"
                          onClick={() => deleteSource.mutate(source.id)}
                          disabled={deleteSource.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}

          {(sources ?? []).length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <p>No sources configured yet.</p>
              <p className="text-sm">Click "Add Source" to get started.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
