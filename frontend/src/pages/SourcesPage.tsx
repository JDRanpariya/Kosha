import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Plus, Trash2, RefreshCw, Check, X, Youtube } from 'lucide-react'
import { Pause, Play } from 'lucide-react'
import {
    useSources,
    useCreateSource,
    useDeleteSource,
    useTriggerIngestion,
    useUpdateSource,
} from '@/hooks/useSources'
import { formatDate, cn } from '@/lib/utils'
import type { Source } from '@/types'

/* ─── Source type metadata ─────────────────────────────────────────────── */
const SOURCE_TYPES = [
    { value: 'rss', label: 'RSS Feed', category: 'newsletters', placeholder: 'Feed URL', configRequired: true },
    { value: 'substack', label: 'Substack', category: 'newsletters', placeholder: 'Publication URL', configRequired: true },
    { value: 'email_imap', label: 'Email newsletter', category: 'newsletters', placeholder: 'IMAP host (imap.gmail.com)', configRequired: true },
    { value: 'arxiv', label: 'arXiv', category: 'papers', placeholder: 'Categories (cs.AI,stat.ML)', configRequired: true },
    { value: 'hackernews', label: 'Hacker News', category: 'social', placeholder: 'Tag (front_page, ask_hn…)', configRequired: false },
    { value: 'reddit', label: 'Reddit', category: 'social', placeholder: 'Subreddits (MachineLearning,LocalLLaMA)', configRequired: true },
    { value: 'github', label: 'GitHub', category: 'dev', placeholder: 'Repos (owner/repo) — blank for trending', configRequired: false },
    { value: 'spotify', label: 'Spotify podcast', category: 'podcasts', placeholder: 'Show ID', configRequired: true },
    { value: 'youtube', label: 'YouTube channel', category: 'videos', placeholder: 'Channel IDs (UCxxx,UCyyy)', configRequired: true },
    { value: 'youtube_subscriptions', label: 'YouTube subscriptions', category: 'videos', placeholder: '', configRequired: null },
] as const

const CATEGORY_ORDER = ['newsletters', 'papers', 'social', 'dev', 'podcasts', 'videos']

const CATEGORY_DOTS: Record<string, string> = {
    newsletters: 'bg-amber-500',
    papers: 'bg-blue-500',
    social: 'bg-orange-500',
    dev: 'bg-gray-500',
    podcasts: 'bg-green-500',
    videos: 'bg-red-500',
}

function buildConfig(type: string, value: string): Record<string, unknown> {
    const v = value.trim()
    switch (type) {
        case 'rss': return { feed_url: v }
        case 'substack': return { publication_url: v }
        case 'arxiv': return { categories: v.split(',').map(s => s.trim()).filter(Boolean) }
        case 'hackernews': return { tags: v || 'front_page' }
        case 'reddit': return { subreddits: v.split(',').map(s => s.trim()).filter(Boolean) }
        case 'github': return { repos: v ? v.split(',').map(s => s.trim()).filter(Boolean) : [], fetch_trending: true }
        case 'spotify': return { show_id: v }
        case 'youtube': return { channels: v.split(',').map(s => s.trim()).filter(Boolean) }
        default: return {}
    }
}

/* ─── Add form ─────────────────────────────────────────────────────────── */
function AddForm({ onClose }: { onClose: () => void }) {
    const create = useCreateSource()
    const [form, setForm] = useState({ name: '', type: 'rss', config: '' })
    const meta = SOURCE_TYPES.find(t => t.value === form.type)
    const isOAuth = meta?.configRequired === null

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (isOAuth) { window.location.href = '/api/youtube/oauth/start'; return }
        create.mutate(
            { name: form.name, type: form.type, url: form.type === 'rss' ? form.config : undefined, config_json: buildConfig(form.type, form.config) },
            { onSuccess: onClose }
        )
    }

    const grouped = [...SOURCE_TYPES].reduce<Record<string, typeof SOURCE_TYPES[number][]>>((acc, t) => {
        if (!acc[t.category]) acc[t.category] = []
        acc[t.category].push(t)
        return acc
    }, {})

    return (
        <div className="card-kosha p-5 mb-6 fade-up">
            <h2 className="font-serif text-lg mb-4">Add source</h2>
            <form onSubmit={handleSubmit} className="space-y-4">

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="block text-xs text-ink-faint mb-1.5 uppercase tracking-wider">Name</label>
                        <input
                            value={form.name}
                            onChange={e => setForm({ ...form, name: e.target.value })}
                            placeholder="My source"
                            required
                            className="w-full h-9 px-3 rounded-md border border-border bg-parchment-mid text-sm text-ink placeholder:text-ink-faint outline-none focus:border-ink-faint transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-ink-faint mb-1.5 uppercase tracking-wider">Type</label>
                        <select
                            value={form.type}
                            onChange={e => setForm({ ...form, type: e.target.value, config: '' })}
                            className="w-full h-9 px-3 rounded-md border border-border bg-parchment-mid text-sm text-ink outline-none focus:border-ink-faint transition-colors"
                        >
                            {CATEGORY_ORDER.filter(c => grouped[c]).map(cat => (
                                <optgroup key={cat} label={cat.charAt(0).toUpperCase() + cat.slice(1)}>
                                    {grouped[cat].map(t => (
                                        <option key={t.value} value={t.value}>{t.label}</option>
                                    ))}
                                </optgroup>
                            ))}
                        </select>
                    </div>
                </div>

                {isOAuth ? (
                    <div className="rounded-md border border-sage-light bg-sage-light/30 p-3 text-sm text-ink-mid">
                        Clicking connect will open Google's permission screen and import all your subscriptions automatically.
                    </div>
                ) : meta && (
                    <div>
                        <label className="block text-xs text-ink-faint mb-1.5 uppercase tracking-wider">
                            Configuration {meta.configRequired === false && <span className="normal-case">(optional)</span>}
                        </label>
                        <input
                            value={form.config}
                            onChange={e => setForm({ ...form, config: e.target.value })}
                            placeholder={meta.placeholder}
                            required={meta.configRequired === true}
                            className="w-full h-9 px-3 rounded-md border border-border bg-parchment-mid text-sm text-ink placeholder:text-ink-faint outline-none focus:border-ink-faint transition-colors"
                        />
                    </div>
                )}

                <div className="flex gap-2 pt-1">
                    {isOAuth ? (
                        <button type="submit" className="flex items-center gap-2 px-4 py-2 rounded-md bg-red-600 text-white text-sm hover:bg-red-700 transition-colors">
                            <Youtube className="h-3.5 w-3.5" />
                            Connect with Google
                        </button>
                    ) : (
                        <button
                            type="submit"
                            disabled={create.isPending}
                            className="px-4 py-2 rounded-md bg-ink text-background text-sm hover:bg-ink-mid transition-colors disabled:opacity-40"
                        >
                            {create.isPending ? 'Adding…' : 'Add source'}
                        </button>
                    )}
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 rounded-md border border-border text-sm text-ink-mid hover:text-ink hover:bg-parchment-deep transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    )
}

/* ─── Source row ───────────────────────────────────────────────────────── */
function SourceRow({ source }: { source: Source }) {
    const update = useUpdateSource()
    const remove = useDeleteSource()
    const trigger = useTriggerIngestion()
    const cat = SOURCE_TYPES.find(t => t.value === source.type)?.category ?? 'other'
    const dot = CATEGORY_DOTS[cat] ?? 'bg-gray-400'

    return (
        <div className="card-kosha p-4 flex items-center gap-4 group">
            {/* Dot indicator */}
            <div className={cn('w-2 h-2 rounded-full shrink-0 mt-0.5', dot, !source.enabled && 'opacity-30')} />

            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-ink">{source.name}</span>
                    {!source.enabled && (
                        <span className="source-badge text-ink-faint">paused</span>
                    )}
                </div>
                <p className="text-xs text-ink-faint mt-0.5 truncate">
                    {source.type === 'youtube_subscriptions' ? 'OAuth — subscriptions' : (source.url ?? JSON.stringify(source.config_json))}
                </p>
                {source.last_fetched_at && (
                    <p className="text-xs text-ink-faint/60 mt-0.5">
                        Last synced {formatDate(source.last_fetched_at)}
                    </p>
                )}
            </div>

            {/* Actions — shown on hover */}
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    title={source.enabled ? 'Pause' : 'Resume'}
                    onClick={() => update.mutate({ id: source.id, data: { enabled: !source.enabled } })}
                    className="p-1.5 rounded text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors"
                >
                    {source.enabled
                        ? <Pause className="h-3.5 w-3.5" />   // "click to pause"
                        : <Play className="h-3.5 w-3.5" />   // "click to resume"
                    }
                </button>

                <button
                    title="Fetch now"
                    onClick={() => trigger.mutate(source.id)}
                    disabled={trigger.isPending}
                    className="p-1.5 rounded text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors"
                >
                    <RefreshCw className={cn('h-3.5 w-3.5', trigger.isPending && 'animate-spin')} />
                </button>

                <button
                    title="Remove"
                    onClick={() => { if (confirm(`Remove "${source.name}"?`)) remove.mutate(source.id) }}
                    className="p-1.5 rounded text-ink-faint hover:text-red-500 hover:bg-parchment-deep transition-colors"
                >
                    <Trash2 className="h-3.5 w-3.5" />
                </button>
            </div>
        </div>
    )
}

/* ─── Page ─────────────────────────────────────────────────────────────── */
export function SourcesPage() {
    const [params] = useSearchParams()
    const { data: sources = [], isLoading, isError } = useSources()
    const [showForm, setShowForm] = useState(false)
    const [oauthOk, setOauthOk] = useState(false)

    useEffect(() => {
        if (params.get('youtube_connected') === '1') {
            setOauthOk(true)
            setTimeout(() => setOauthOk(false), 6000)
        }
    }, [params])

    // Group by category
    const grouped = sources.reduce<Record<string, Source[]>>((acc, s) => {
        const cat = SOURCE_TYPES.find(t => t.value === s.type)?.category ?? 'other'
        if (!acc[cat]) acc[cat] = []
        acc[cat].push(s)
        return acc
    }, {})

    const sortedCats = [
        ...CATEGORY_ORDER.filter(c => grouped[c]),
        ...Object.keys(grouped).filter(c => !CATEGORY_ORDER.includes(c)),
    ]

    return (
        <>
            {/* Header */}
            <div className="flex items-end justify-between mb-8 fade-up">
                <div>
                    <p className="text-xs uppercase tracking-[0.15em] text-ink-faint font-medium mb-1">Manage</p>
                    <h1 className="font-serif text-3xl font-normal text-ink">Sources</h1>
                </div>
                <button
                    onClick={() => setShowForm(v => !v)}
                    className="flex items-center gap-2 px-4 py-2 rounded-md bg-ink text-background text-sm hover:bg-ink-mid transition-colors"
                >
                    <Plus className="h-3.5 w-3.5" />
                    Add source
                </button>
            </div>

            {/* OAuth success */}
            {oauthOk && (
                <div className="mb-4 rounded-md border border-sage-light bg-sage-light/40 px-4 py-3 text-sm text-sage-dark flex justify-between items-center fade-up">
                    YouTube subscriptions connected.
                    <button onClick={() => setOauthOk(false)}><X className="h-3.5 w-3.5" /></button>
                </div>
            )}

            {showForm && <AddForm onClose={() => setShowForm(false)} />}

            {isLoading && (
                <div className="space-y-3">
                    {[0, 1, 2].map(i => (
                        <div key={i} className="card-kosha p-4 h-16 skeleton-warm" />
                    ))}
                </div>
            )}

            {isError && (
                <p className="text-sm text-ink-faint py-8 text-center">
                    Could not reach the backend. Is it running?
                </p>
            )}

            {!isLoading && !isError && (
                <div className="space-y-8">
                    {sortedCats.map(cat => (
                        <div key={cat}>
                            <div className="section-divider" style={{ opacity: 1 }}>
                                {cat}
                            </div>
                            <div className="space-y-2">
                                {grouped[cat].map(s => <SourceRow key={s.id} source={s} />)}
                            </div>
                        </div>
                    ))}

                    {sources.length === 0 && (
                        <div className="flex flex-col items-center py-20 gap-3 text-center">
                            <svg width="32" height="32" viewBox="0 0 20 20" fill="none" className="text-ink-faint/30">
                                <path d="M3 17C3 17 5 10 10 7C15 4 17 3 17 3C17 3 16 5 13 10C10 15 3 17 3 17Z" fill="currentColor" />
                            </svg>
                            <p className="text-sm text-ink-faint">No sources yet.</p>
                            <button onClick={() => setShowForm(true)} className="text-sm text-sage hover:underline underline-offset-4">
                                Add your first source →
                            </button>
                        </div>
                    )}
                </div>
            )}
        </>
    )
}
