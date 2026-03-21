import { Search, Menu, Moon, Sun, RefreshCw } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useUIStore } from '@/stores/uiStore'
import { useTriggerIngestion } from '@/hooks/useSources'

export function Header() {
    const [searchQuery, setSearchQuery] = useState('')
    const navigate = useNavigate()
    const { toggleSidebar, toggleTheme, theme } = useUIStore()
    const triggerIngestion = useTriggerIngestion()

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`)
        }
    }

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-14 items-center px-4 gap-4">
                <Button variant="ghost" size="icon" onClick={toggleSidebar} className="md:hidden">
                    <Menu className="h-5 w-5" />
                </Button>

                <Link to="/" className="flex items-center gap-2 font-semibold">
                    <span className="text-xl">📚</span>
                    <span className="hidden sm:inline">Kosha</span>
                </Link>

                <form onSubmit={handleSearch} className="flex-1 max-w-md mx-auto">
                    <div className="relative">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Search content..."
                            className="pl-8"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </form>

                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => triggerIngestion.mutate(undefined)}
                        disabled={triggerIngestion.isPending}
                        title="Refresh all sources"
                    >
                        <RefreshCw className={`h-5 w-5 ${triggerIngestion.isPending ? 'animate-spin' : ''}`} />
                    </Button>

                    <Button variant="ghost" size="icon" onClick={toggleTheme}>
                        {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                    </Button>
                </div>
            </div>
        </header>
    )
}
