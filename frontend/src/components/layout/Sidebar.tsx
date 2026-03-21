import { NavLink, useLocation } from 'react-router-dom'
import { BookOpen, Bookmark, Rss, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/uiStore'
import { useDailyDigestCount } from '@/hooks/useItems'

const NAV = [
  {
    section: 'Consume',
    items: [
      {
        to: '/',
        icon: BookOpen,
        label: "Today's digest",
        badge: 'digest', // pulls live count
      },
    ],
  },
  {
    section: 'Study',
    items: [
      {
        to: '/reading-list',
        icon: Bookmark,
        label: 'Reading list',
        badge: 'saved',
      },
    ],
  },
  {
    section: 'Configure',
    items: [
      { to: '/sources',  icon: Rss,      label: 'Sources'  },
      { to: '/settings', icon: Settings,  label: 'Settings' },
    ],
  },
]

interface BadgeProps {
  type?: string
}

function NavBadge({ type }: BadgeProps) {
  const { digestCount, savedCount } = useDailyDigestCount()

  const count = type === 'digest' ? digestCount : type === 'saved' ? savedCount : 0
  if (!count) return null

  const isDigest = type === 'digest'
  return (
    <span className={cn(
      'ml-auto text-[10px] font-medium px-1.5 py-0.5 rounded-full leading-none',
      isDigest
        ? 'bg-sage text-parchment'
        : 'bg-parchment-deep text-ink-mid'
    )}>
      {count}
    </span>
  )
}

export function Sidebar() {
  const { sidebarOpen } = useUIStore()
  const location = useLocation()

  return (
    <aside className={cn(
      'fixed left-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-52',
      'flex flex-col border-r border-border bg-background',
      'transition-transform duration-300 ease-in-out md:translate-x-0',
      sidebarOpen ? 'translate-x-0' : '-translate-x-full'
    )}>
      <nav className="flex-1 overflow-y-auto py-3 px-2.5">
        {NAV.map(({ section, items }) => (
          <div key={section} className="mb-5">
            <p className="px-2 mb-1.5 text-[9px] font-medium tracking-[0.12em] uppercase text-ink-faint">
              {section}
            </p>
            {items.map(({ to, icon: Icon, label, badge }) => {
              const isActive = to === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(to)

              return (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={cn(
                    'flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm',
                    'transition-colors duration-150',
                    isActive
                      ? 'bg-sage-light text-sage-dark font-medium'
                      : 'text-ink-mid hover:bg-parchment-deep hover:text-ink'
                  )}
                >
                  <Icon className="h-[14px] w-[14px] shrink-0 opacity-75" />
                  <span className="flex-1 leading-none">{label}</span>
                  {badge && <NavBadge type={badge} />}
                </NavLink>
              )
            })}
          </div>
        ))}
      </nav>

      {/* Phase indicator — honest about where the system is */}
      <div className="px-4 py-3 border-t border-border">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-sage opacity-80" />
          <p className="text-[10px] text-ink-faint">Manual curation · Phase 1</p>
        </div>
      </div>
    </aside>
  )
}
