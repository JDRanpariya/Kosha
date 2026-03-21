import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  toggleTheme: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'light',

      toggleSidebar: () =>
        set(s => ({ sidebarOpen: !s.sidebarOpen })),

      setSidebarOpen: (open) =>
        set({ sidebarOpen: open }),

      toggleTheme: () =>
        set(s => {
          const next = s.theme === 'light' ? 'dark' : 'light'
          // Apply to document immediately
          document.documentElement.classList.toggle('dark', next === 'dark')
          return { theme: next }
        }),
    }),
    {
      name: 'kosha-ui',
      // Only persist sidebar state and theme — not transient UI state
      partialize: s => ({ sidebarOpen: s.sidebarOpen, theme: s.theme }),
      onRehydrateStorage: () => state => {
        // Sync document class on page load
        if (state?.theme === 'dark') {
          document.documentElement.classList.add('dark')
        }
      },
    }
  )
)
