import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { DigestPage } from '@/pages/DigestPage'
import { SearchPage } from '@/pages/SearchPage'
import { ReadingListPage } from '@/pages/ReadingListPage'
import { SourcesPage } from '@/pages/SourcesPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { Toaster } from '@/components/ui/toast'

function App() {
    return (
        <>
            <Layout>
                <Routes>
                    <Route path="/" element={<DigestPage />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/reading-list" element={<ReadingListPage />} />
                    <Route path="/sources" element={<SourcesPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/saved" element={<ReadingListPage />} />
                </Routes>
            </Layout>
            <Toaster />
        </>
    )
}

export default App
