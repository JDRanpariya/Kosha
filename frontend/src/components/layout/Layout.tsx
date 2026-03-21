import { ReactNode } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/lib/utils'

interface LayoutProps {
    children: ReactNode
}

export function Layout({ children }: LayoutProps) {
    const { sidebarOpen } = useUIStore()

    return (
        <div className="min-h-screen bg-background">
            <Header />
            <Sidebar />
            <main
                className={cn(
                    'transition-all duration-300 pt-4 px-4 pb-8',
                    sidebarOpen ? 'md:ml-64' : ''
                )}
            >
                <div className="mx-auto max-w-4xl">{children}</div>
            </main>
        </div>
    )
}
