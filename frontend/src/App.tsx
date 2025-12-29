import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import UploadForm from './components/UploadForm'
import StyleSelector from './components/StyleSelector'
import ProgressTracker from './components/ProgressTracker'

const queryClient = new QueryClient()

function App() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [selectedStyle, setSelectedStyle] = useState('cinematic_drama')

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <header className="bg-slate-800 shadow-lg border-b border-slate-700">
          <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-bold text-white">🎬 AI Video Editor</h1>
            <p className="text-slate-300 mt-2">Create professional videos with AI-powered editing</p>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          {!jobId ? (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Upload Section */}
                <div className="bg-slate-700 rounded-lg shadow-lg p-8 border border-slate-600">
                  <h2 className="text-2xl font-bold text-white mb-6">Upload Media</h2>
                  <UploadForm onJobCreated={setJobId} style={selectedStyle} />
                </div>

                {/* Style Selection */}
                <div className="bg-slate-700 rounded-lg shadow-lg p-8 border border-slate-600">
                  <h2 className="text-2xl font-bold text-white mb-6">Choose Style</h2>
                  <StyleSelector selectedStyle={selectedStyle} onStyleChange={setSelectedStyle} />
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-700 rounded-lg shadow-lg p-8 border border-slate-600">
              <h2 className="text-2xl font-bold text-white mb-6">Processing Video</h2>
              <ProgressTracker jobId={jobId} onComplete={() => setJobId(null)} />
            </div>
          )}
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
