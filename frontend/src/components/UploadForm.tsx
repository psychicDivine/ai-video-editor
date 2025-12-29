import { useState } from 'react'
import axios from 'axios'
import MusicTimeline from './MusicTimeline'

interface UploadFormProps {
  onJobCreated: (jobId: string) => void
  style: string
}

export default function UploadForm({ onJobCreated, style }: UploadFormProps) {
  const [videos, setVideos] = useState<File[]>([])
  const [music, setMusic] = useState<File | null>(null)
  const [musicStartTime, setMusicStartTime] = useState(0)
  const [musicEndTime, setMusicEndTime] = useState(30)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setVideos(Array.from(e.target.files))
    }
  }

  const handleMusicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0]
      setMusic(file)
    }
  }

  const handleTimeSelect = (startTime: number, endTime: number) => {
    setMusicStartTime(startTime)
    setMusicEndTime(endTime)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (videos.length === 0 || !music) {
      setError('Please select videos and music')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      videos.forEach((video) => {
        formData.append('videos', video)
      })
      formData.append('music', music)
      formData.append('style', style)
      formData.append('music_start_time', musicStartTime.toString())
      formData.append('music_end_time', musicEndTime.toString())

      const response = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      onJobCreated(response.data.job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Video Upload */}
      <div>
        <label className="block text-sm font-medium text-slate-200 mb-2">
          📹 Videos (Select Multiple)
        </label>
        <input
          type="file"
          multiple
          accept="video/*"
          onChange={handleVideoChange}
          className="block w-full text-sm text-slate-300
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-600 file:text-white
            hover:file:bg-blue-700"
        />
        {videos.length > 0 && (
          <div className="mt-3 bg-blue-900 bg-opacity-30 p-3 rounded border border-blue-600">
            <p className="text-sm text-slate-300 font-semibold mb-2">
              ✅ {videos.length} video(s) selected:
            </p>
            <ul className="text-xs text-slate-400 space-y-1">
              {videos.map((v, i) => (
                <li key={i}>• {v.name}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Music Upload */}
      <div>
        <label className="block text-sm font-medium text-slate-200 mb-2">
          🎵 Music Track (Select One)
        </label>
        <input
          type="file"
          accept="audio/*"
          onChange={handleMusicChange}
          className="block w-full text-sm text-slate-300
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-green-600 file:text-white
            hover:file:bg-green-700"
        />
        {music && (
          <div className="mt-3 bg-green-900 bg-opacity-30 p-4 rounded border border-green-600">
            <p className="text-sm text-slate-300 font-semibold mb-4">
              ✅ Music: {music.name}
            </p>
            <MusicTimeline musicFile={music} onTimeSelect={handleTimeSelect} />
          </div>
        )}
      </div>

      {/* Workflow Info */}
      <div className="bg-slate-600 bg-opacity-50 p-4 rounded-lg border border-slate-500">
        <p className="text-sm text-slate-300">
          <span className="font-semibold">How it works:</span>
        </p>
        <ol className="text-xs text-slate-400 mt-2 space-y-1 ml-4">
          <li>1. Upload your video clips (will be combined)</li>
          <li>2. Upload your music track (will be synced to beats)</li>
          <li>3. Choose video duration (10-60 seconds)</li>
          <li>4. AI will cut and sync videos to music beats</li>
          <li>5. Download your finished video!</li>
        </ol>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || videos.length === 0 || !music}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition"
      >
        {loading ? '⏳ Processing...' : '🚀 Create Video'}
      </button>
    </form>
  )
}
