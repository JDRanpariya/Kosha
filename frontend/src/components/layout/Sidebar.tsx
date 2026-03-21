import { NavLink } from 'react-router-dom'
import { Home, Search, Bookmark, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/uiStore'

const navItems = [
    { to: '/', icon: Home, label: 'Daily Digest' },
    { to: '/search', icon: Search, label: 'Search' },
    { to: '/saved', icon: Bookmark, label: 'Saved' },
    { to: '/sources', icon: Settings, label: 'Sources' },
]

export function Sidebar() {
    const { sidebarOpen } = useUIStore()

    return (
        <aside
            className={cn(
                'fixed left-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-64 border-r bg-background transition-transform duration-300 md:translate-x-0',
                sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            )}
        >
            <nav className="flex flex-col gap-1 p-4">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground',
                                isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
                            )
                        }
                    >
                        <Icon className="h-4 w-4" />
                        {label}
                    </NavLink>
                ))}
            </nav>
        </aside>
    )
}
