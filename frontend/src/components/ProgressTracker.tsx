import { useEffect, useState } from 'react'
import axios from 'axios'

interface ProgressTrackerProps {
  jobId: string
  onComplete: () => void
}

interface JobStatus {
  status: string
  progress: number
  current_step: string | null
  error_message: string | null
  output_video_url: string | null
}

export default function ProgressTracker({ jobId, onComplete }: ProgressTrackerProps) {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/jobs/${jobId}`)
        setJobStatus(response.data)
        setLoading(false)

        if (response.data.status === 'COMPLETED') {
          setTimeout(() => {
            onComplete()
          }, 2000)
        } else if (response.data.status === 'FAILED') {
          setError(response.data.error_message || 'Processing failed')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
        setLoading(false)
      }
    }

    const interval = setInterval(pollStatus, 1000)
    pollStatus()

    return () => clearInterval(interval)
  }, [jobId, onComplete])

  if (loading) {
    return <div className="text-center text-slate-300">Loading...</div>
  }

  if (error) {
    return (
      <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
        {error}
      </div>
    )
  }

  if (!jobStatus) {
    return <div className="text-center text-slate-300">No status available</div>
  }

  const statusColors = {
    PENDING: 'bg-slate-600',
    UPLOADING: 'bg-yellow-600',
    PROCESSING: 'bg-blue-600',
    COMPLETED: 'bg-green-600',
    FAILED: 'bg-red-600',
  }

  const statusColor = statusColors[jobStatus.status as keyof typeof statusColors] || 'bg-slate-600'

  return (
    <div className="space-y-6">
      {/* Status Badge */}
      <div className="flex items-center gap-3">
        <div className={`${statusColor} text-white px-4 py-2 rounded-full font-bold`}>
          {jobStatus.status}
        </div>
        <span className="text-slate-300">{jobStatus.progress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-600 rounded-full h-4 overflow-hidden">
        <div
          className={`${statusColor} h-full transition-all duration-300`}
          style={{ width: `${jobStatus.progress}%` }}
        />
      </div>

      {/* Current Step */}
      {jobStatus.current_step && (
        <div className="bg-slate-600 bg-opacity-50 p-4 rounded-lg">
          <p className="text-sm text-slate-300">
            <span className="font-semibold">Current Step:</span> {jobStatus.current_step}
          </p>
        </div>
      )}

      {/* Download Button */}
      {jobStatus.status === 'COMPLETED' && jobStatus.output_video_url && (
        <a
          href={jobStatus.output_video_url}
          download
          className="block w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition"
        >
          ⬇️ Download Video
        </a>
      )}

      {/* Error Message */}
      {jobStatus.status === 'FAILED' && jobStatus.error_message && (
        <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
          {jobStatus.error_message}
        </div>
      )}
    </div>
  )
}
