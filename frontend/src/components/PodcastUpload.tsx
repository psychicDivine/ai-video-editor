import { useState } from 'react'
import axios from 'axios'

interface PodcastUploadProps {
  onJobCreated: (jobId: string) => void
}

export default function PodcastUpload({ onJobCreated }: PodcastUploadProps) {
  const [title, setTitle] = useState('')
  const [audio, setAudio] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAudioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setAudio(e.target.files[0])
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!audio) {
      setError('Please select an audio file')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', audio)
      formData.append('title', title)

      const resp = await axios.post('/api/podcast', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      onJobCreated(resp.data.job_id)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const data = err.response?.data as any
        const msg = data?.message || data?.detail || data?.error || err.message || 'Upload failed'
        setError(String(msg))
      } else {
        setError(err instanceof Error ? err.message : 'Upload failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-200 mb-2">Podcast Title</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Episode title"
          className="w-full px-3 py-2 rounded bg-slate-800 text-white border border-slate-700"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-200 mb-2">Audio File</label>
        <input type="file" accept="audio/*" onChange={handleAudioChange} className="block w-full text-sm text-slate-300" />
        {audio && <p className="mt-2 text-xs text-slate-400">Selected: {audio.name}</p>}
      </div>

      {error && <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-2 rounded">{error}</div>}

      <button
        type="submit"
        disabled={loading || !audio}
        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-lg"
      >
        {loading ? '⏳ Processing...' : '📤 Upload Podcast'}
      </button>
    </form>
  )
}
