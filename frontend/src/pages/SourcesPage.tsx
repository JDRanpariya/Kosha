import { useState } from 'react'
import { Plus, Trash2, RefreshCw, Check, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useSources, useCreateSource, useDeleteSource, useTriggerIngestion, useUpdateSource } from '@/hooks/useSources'
import { formatDate } from '@/lib/utils'

const SOURCE_TYPES = [
    { value: 'rss', label: 'RSS Feed', placeholder: 'Feed URL' },
    { value: 'arxiv', label: 'arXiv', placeholder: 'Categories (e.g., cs.AI,stat.ML)' },
    { value: 'spotify', label: 'Spotify Podcast', placeholder: 'Show ID' },
    { value: 'youtube', label: 'YouTube Channel', placeholder: 'Channel ID' },
]

export function SourcesPage() {
    const { data: sources, isLoading } = useSources()
    const createSource = useCreateSource()
    const deleteSource = useDeleteSource()
    const updateSource = useUpdateSource()
    const triggerIngestion = useTriggerIngestion()

    const [showForm, setShowForm] = useState(false)
    const [formData, setFormData] = useState({
        name: '',
        type: 'rss',
        config: '',
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()

        let config_json: Record<string, unknown> = {}

        if (formData.type === 'rss') {
            config_json = { feed_url: formData.config }
        } else if (formData.type === 'arxiv') {
            config_json = { categories: formData.config.split(',').map((s) => s.trim()) }
        } else if (formData.type === 'spotify') {
            config_json = { show_id: formData.config }
        } else if (formData.type === 'youtube') {
            config_json = { channels: formData.config.split(',').map((s) => s.trim()) }
        }

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

    const getConfigPlaceholder = () => {
        return SOURCE_TYPES.find((t) => t.value === formData.type)?.placeholder ?? ''
    }

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold">Content Sources</h1>
                    <p className="text-muted-foreground">Manage your RSS feeds, podcasts, and channels</p>
                </div>
                <Button onClick={() => setShowForm(!showForm)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Source
                </Button>
            </div>

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
                                    placeholder="My RSS Feed"
                                    required
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Type</label>
                                <select
                                    className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                >
                                    {SOURCE_TYPES.map((type) => (
                                        <option key={type.value} value={type.value}>
                                            {type.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="text-sm font-medium">Configuration</label>
                                <Input
                                    value={formData.config}
                                    onChange={(e) => setFormData({ ...formData, config: e.target.value })}
                                    placeholder={getConfigPlaceholder()}
                                    required
                                />
                            </div>
                            <div className="flex gap-2">
                                <Button type="submit" disabled={createSource.isPending}>
                                    {createSource.isPending ? 'Adding...' : 'Add Source'}
                                </Button>
                                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                                    Cancel
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {isLoading ? (
                <p>Loading sources...</p>
            ) : (
                <div className="space-y-4">
                    {sources?.map((source) => (
                        <Card key={source.id}>
                            <CardContent className="flex items-center justify-between p-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold">{source.name}</h3>
                                        <Badge variant="outline">{source.type}</Badge>
                                        <Badge variant={source.enabled ? 'default' : 'secondary'}>
                                            {source.enabled ? 'Active' : 'Disabled'}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {source.url || JSON.stringify(source.config)}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        Last fetched: {source.last_fetched_at ? formatDate(source.last_fetched_at) : 'Never'}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => updateSource.mutate({ id: source.id, data: { enabled: !source.enabled } })}
                                        title={source.enabled ? 'Disable' : 'Enable'}
                                    >
                                        {source.enabled ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => triggerIngestion.mutate(source.id)}
                                        disabled={triggerIngestion.isPending}
                                        title="Refresh source"
                                    >
                                        <RefreshCw className={`h-4 w-4 ${triggerIngestion.isPending ? 'animate-spin' : ''}`} />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => deleteSource.mutate(source.id)}
                                        disabled={deleteSource.isPending}
                                        title="Delete source"
                                    >
                                        <Trash2 className="h-4 w-4 text-destructive" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}

                    {sources?.length === 0 && (
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
