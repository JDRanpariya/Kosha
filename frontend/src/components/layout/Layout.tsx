import { type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/lib/utils'

// Pages that use the full-height split layout (no outer padding)
const SPLIT_LAYOUT_ROUTES = ['/', '/reading-list']

export function Layout({ children }: { children: ReactNode }) {
  const { sidebarOpen } = useUIStore()
  const { pathname } = useLocation()

  const isSplitLayout = SPLIT_LAYOUT_ROUTES.includes(pathname)

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <Sidebar />

      <div className={cn(
        'transition-all duration-300 ease-in-out',
        sidebarOpen ? 'md:ml-52' : 'ml-0',
      )}>
        {isSplitLayout ? (
          // Split-layout pages manage their own internal padding and overflow
          <div className="h-[calc(100vh-3.5rem)] overflow-hidden">
            {children}
          </div>
        ) : (
          // Standard pages: comfortable reading width with padding
          <main className="px-6 pt-7 pb-16">
            <div className="mx-auto max-w-2xl">
              {children}
            </div>
          </main>
        )}
      </div>
    </div>
  )
}
