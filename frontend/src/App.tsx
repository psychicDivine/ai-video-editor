import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import './App.css'
import ReelEditor from './components/Studio/ReelEditor'
import PodcastEditor from './components/Studio/PodcastEditor'
import ProgressTracker from './components/ProgressTracker'
import { AppProvider, useApp } from './context/AppContext'
import RootLayout from './components/Layout/RootLayout'
import Button from './ui/Button'
import { setDocumentTitle } from './config/brand'

const queryClient = new QueryClient()

function AppContent() {
  const { viewMode, jobId, setJobId } = useApp()

  return (
    <RootLayout>
      <div className="h-full overflow-hidden">
        {!jobId ? (
          <div className="h-full">
            {viewMode === 'reel' ? (
              <div className="h-full">
                <ReelEditor
                  onJobCreated={setJobId}
                  style="cinematic_drama"
                />
              </div>
            ) : viewMode === 'podcast' ? (
              <div className="max-w-5xl mx-auto p-8">
                <PodcastEditor onJobCreated={setJobId} />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-text-muted">
                <SparkleEmptyState />
              </div>
            )}
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            <div className="bg-surface p-8 rounded-3xl border border-border shadow-2xl">
              <header className="mb-6">
                <h2 className="text-2xl font-display font-bold text-text-primary">Orchestrating AI Pipeline</h2>
                <p className="text-xs text-text-secondary font-mono">JOB_ID: {jobId}</p>
              </header>

              <ProgressTracker jobId={jobId} onComplete={() => { }} />

              <div className="mt-8 pt-6 border-t border-border flex justify-end">
                <Button variant="secondary" onClick={() => setJobId(null)}>
                  Back to Workspace
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </RootLayout>
  )
}

function SparkleEmptyState() {
  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-full bg-surface-elevated flex items-center justify-center mx-auto mb-4 border border-border">
        <span className="text-2xl">✨</span>
      </div>
      <p className="text-sm font-medium">This module is being fine-tuned.</p>
      <p className="text-xs text-text-muted mt-1">Check back soon for the full experience.</p>
    </div>
  )
}

function App() {
  useEffect(() => {
    setDocumentTitle()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </QueryClientProvider>
  )
}

export default App
