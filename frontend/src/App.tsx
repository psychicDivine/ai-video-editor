import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import UploadForm from './components/UploadForm'
import StyleSelector from './components/StyleSelector'
import ProgressTracker from './components/ProgressTracker'
import ThemeToggle from './components/ThemeToggle'
import PodcastUpload from './components/PodcastUpload'

const queryClient = new QueryClient()

function App() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [selectedStyle, setSelectedStyle] = useState('cinematic_drama')
  const [mode, setMode] = useState<'reel' | 'podcast'>('reel')
  const [showComplete, setShowComplete] = useState(false)

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
        <header className="shadow-lg border-b" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white">🎬 AI Video Editor</h1>
              <p className="text-sm text-[var(--muted)] mt-1">Create professional videos with AI-powered editing</p>
            </div>
            <div className="flex items-center gap-3">
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 mobile-stack">
          {!jobId ? (
            <div className="space-y-8">
              <div className="flex gap-4 items-center mb-4">
                <button
                  onClick={() => setMode('reel')}
                  className={`px-4 py-2 rounded-lg font-semibold ${mode === 'reel' ? 'bg-blue-600 text-white' : 'bg-transparent text-[var(--muted)] border border-transparent hover:bg-blue-500/10'}`}
                >
                  Reel
                </button>
                <button
                  onClick={() => setMode('podcast')}
                  className={`px-4 py-2 rounded-lg font-semibold ${mode === 'podcast' ? 'bg-green-600 text-white' : 'bg-transparent text-[var(--muted)] border border-transparent hover:bg-green-500/10'}`}
                >
                  Podcast
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {mode === 'reel' ? (
                  <>
                    {/* Upload Section */}
                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Upload Media</h2>
                      <UploadForm onJobCreated={setJobId} style={selectedStyle} />
                    </div>

                    {/* Style Selection */}
                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Choose Style</h2>
                      <StyleSelector selectedStyle={selectedStyle} onStyleChange={setSelectedStyle} />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Podcast Upload</h2>
                      <PodcastUpload onJobCreated={setJobId} />
                    </div>

                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Podcast Tips</h2>
                      <p className="text-sm text-[var(--muted)]">Upload a single high-quality audio file (mp3/wav). We will extract transcript, fillers and highlights. Use a quiet recording for best results.</p>
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <h2 className="text-2xl font-bold text-white mb-6">Processing Video</h2>
              <ProgressTracker jobId={jobId} onComplete={() => setShowComplete(true)} />

              {showComplete && (
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => {
                      // User chooses to return to main upload screen
                      setJobId(null)
                      setShowComplete(false)
                    }}
                    className="px-4 py-2 rounded bg-slate-600 text-white"
                  >
                    Back to Uploads
                  </button>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
