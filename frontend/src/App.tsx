import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { DigestPage } from '@/pages/DigestPage'
import { SearchPage } from '@/pages/SearchPage'
import { SavedPage } from '@/pages/SavedPage'
import { SourcesPage } from '@/pages/SourcesPage'
import { Toaster } from '@/components/ui/toast'

function App() {
    return (
        <>
            <Layout>
                <Routes>
                    <Route path="/" element={<DigestPage />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/saved" element={<SavedPage />} />
                    <Route path="/sources" element={<SourcesPage />} />
                </Routes>
            </Layout>
            <Toaster />
        </>
    )
}

export default App
