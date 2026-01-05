import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import UploadForm from './components/UploadForm'
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

        <main className="w-full h-[calc(100vh-80px)] overflow-hidden bg-[#0b0f14]">
          {!jobId ? (
            <div className="h-full flex flex-col">
              {/* Mode Switcher - Floating or Top Bar */}
              <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-[#0b0f14]/50 backdrop-blur-sm z-10">
                <div className="flex gap-2 bg-black/40 p-1 rounded-lg border border-white/5">
                  <button
                    type="button"
                    onClick={() => setMode('reel')}
                    className={`px-6 py-2 rounded-md text-sm font-mono tracking-wider transition-all ${mode === 'reel' ? 'bg-neon-blue/20 text-neon-blue shadow-[0_0_15px_rgba(0,240,255,0.1)]' : 'text-slate-400 hover:text-white'}`}
                  >
                    REEL
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('podcast')}
                    className={`px-6 py-2 rounded-md text-sm font-mono tracking-wider transition-all ${mode === 'podcast' ? 'bg-neon-green/20 text-neon-green shadow-[0_0_15px_rgba(57,255,122,0.1)]' : 'text-slate-400 hover:text-white'}`}
                  >
                    PODCAST
                  </button>
                </div>
                <div className="text-xs font-mono text-slate-500">
                  STUDIO MODE: ACTIVE
                </div>
              </div>

              <div className="flex-1 overflow-hidden relative">
                {mode === 'reel' ? (
                  <UploadForm 
                    onJobCreated={setJobId} 
                    style={selectedStyle} 
                    onStyleChange={setSelectedStyle}
                  />
                ) : (
                  <div className="max-w-4xl mx-auto p-8 grid grid-cols-1 gap-8">
                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Podcast Upload</h2>
                      <PodcastUpload onJobCreated={setJobId} />
                    </div>

                    <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                      <h2 className="text-2xl font-bold text-white mb-6">Podcast Tips</h2>
                      <p className="text-sm text-[var(--muted)]">Upload a single high-quality audio file (mp3/wav). We will extract transcript, fillers and highlights. Use a quiet recording for best results.</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto py-10 px-4">
              <div className="rounded-lg shadow-lg p-6 border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.04)' }}>
                <h2 className="text-2xl font-bold text-white mb-6">Processing Video</h2>
                <ProgressTracker jobId={jobId} onComplete={() => setShowComplete(true)} />

                {showComplete && (
                  <div className="mt-4 flex gap-2">
                    <button
                      type="button"
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
            </div>
          )}
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
