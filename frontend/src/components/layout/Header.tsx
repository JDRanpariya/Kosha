import { Search, RefreshCw, Moon, Sun, Menu } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useUIStore } from '@/stores/uiStore'
import { useTriggerIngestion } from '@/hooks/useSources'
import { cn } from '@/lib/utils'

export function Header() {
  const [query, setQuery] = useState('')
  const [focused, setFocused] = useState(false)
  const navigate = useNavigate()
  const { toggleSidebar, toggleTheme, theme } = useUIStore()
  const trigger = useTriggerIngestion()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/90 backdrop-blur-sm">
      <div className="flex h-14 items-center gap-4 px-4 md:px-6">

        {/* Sidebar toggle — mobile */}
        <button
          onClick={toggleSidebar}
          className="md:hidden p-1.5 rounded-md text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-4 w-4" />
        </button>

        {/* Wordmark */}
        <Link
          to="/"
          className="flex items-center gap-2 shrink-0 group"
        >
          {/* Leaf mark — simple SVG, no emoji */}
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="text-sage">
            <path
              d="M3 17C3 17 5 10 10 7C15 4 17 3 17 3C17 3 16 5 13 10C10 15 3 17 3 17Z"
              fill="currentColor"
              opacity="0.9"
            />
            <path d="M3 17C6 14 9 11 12 8" stroke="hsl(var(--parchment))" strokeWidth="1" strokeLinecap="round"/>
          </svg>
          <span className="font-serif text-lg text-ink tracking-tight hidden sm:inline">
            Kosha
          </span>
        </Link>

        {/* Search — centre, expands on focus */}
        <form
          onSubmit={handleSearch}
          className="flex-1 max-w-md mx-auto"
        >
          <div className={cn(
            'relative flex items-center gap-2 px-3 h-9 rounded-md border bg-parchment-mid transition-all duration-300',
            focused
              ? 'border-ink-faint shadow-sm'
              : 'border-border'
          )}>
            <Search className="h-3.5 w-3.5 text-ink-faint shrink-0" />
            <input
              type="search"
              placeholder="Search your library…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              className="flex-1 bg-transparent text-sm text-ink placeholder:text-ink-faint outline-none min-w-0"
            />
          </div>
        </form>

        {/* Right actions */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => trigger.mutate(undefined)}
            disabled={trigger.isPending}
            title="Fetch all sources"
            className="p-2 rounded-md text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors disabled:opacity-40"
          >
            <RefreshCw className={cn('h-4 w-4', trigger.isPending && 'animate-spin')} />
          </button>

          <button
            onClick={toggleTheme}
            className="p-2 rounded-md text-ink-faint hover:text-ink hover:bg-parchment-deep transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light'
              ? <Moon className="h-4 w-4" />
              : <Sun  className="h-4 w-4" />
            }
          </button>
        </div>
      </div>
    </header>
  )
}
