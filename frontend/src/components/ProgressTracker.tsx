import { useEffect, useState, useRef } from 'react'
import axios, { AxiosError, Canceler } from 'axios'

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
  const [retryCount, setRetryCount] = useState(0)
  const cancelRef = useRef<Canceler | null>(null)

  useEffect(() => {
    // Poll with exponential backoff on errors
    let mounted = true
    let backoff = 1000

    const pollStatus = async () => {
      try {
        setLoading(true)
        const source = axios.CancelToken.source()
        cancelRef.current = source.cancel
        const response = await axios.get(`/api/jobs/${jobId}`, { cancelToken: source.token })
        if (!mounted) return
        setJobStatus(response.data)
        setLoading(false)
        backoff = 1000

        if (response.data.status === 'COMPLETED') {
          // Immediately notify parent that processing finished (don't wait on completed screen)
          onComplete()
        } else if (response.data.status === 'FAILED') {
          setError(response.data.error_message || 'Processing failed')
        }
      } catch (err) {
        if (axios.isCancel(err)) return
        const msg = err instanceof AxiosError ? (err.response?.data?.error || err.message) : 'Failed to fetch status'
        setError(msg)
        setLoading(false)
        // backoff and retry
        setTimeout(() => {
          backoff = Math.min(backoff * 1.8, 10000)
          setRetryCount((c) => c + 1)
        }, backoff)
      }
    }

    const interval = setInterval(pollStatus, 1200)
    pollStatus()

    return () => {
      mounted = false
      clearInterval(interval)
      if (cancelRef.current) cancelRef.current()
    }
  }, [jobId, onComplete, retryCount])

  if (loading && !jobStatus) {
    return (
      <div className="text-center text-[var(--muted)]">Initializing status…</div>
    )
  }

  if (error && !jobStatus) {
    return (
      <div className="space-y-3">
        <div className="bg-[var(--danger)]/90 text-white px-4 py-3 rounded">
          <div className="font-semibold">Error</div>
          <div className="text-sm mt-1">{error}</div>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setError(null)
              setRetryCount((c) => c + 1)
            }}
            className="px-3 py-2 rounded bg-[var(--accent)] text-white"
          >
            Retry
          </button>
          <button
            type="button"
            onClick={() => onComplete()}
            className="px-3 py-2 rounded border"
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  if (!jobStatus) {
    return <div className="text-center text-[var(--muted)]">No status available</div>
  }

  return (
    <div className="space-y-5">
      {/* Header: status and progress */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1 rounded-full text-white font-semibold`} style={{ background: 'var(--accent)' }}>
            {jobStatus.status}
          </div>
          <div className="text-sm text-[var(--muted)]">{jobStatus.progress}%</div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setRetryCount((c) => c + 1)}
            className="text-sm px-2 py-1 rounded border"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Enhanced Progress Bar */}
      <div className="w-full bg-[var(--glass)] rounded-full h-4 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 progress-stripes`}
          style={{ width: `${jobStatus.progress}%`, backgroundColor: jobStatus.status === 'FAILED' ? 'var(--danger)' : 'var(--accent)' }}
          role="progressbar"
          aria-valuenow={jobStatus.progress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {/* Current Step */}
      {jobStatus.current_step && (
        <div className="p-3 rounded border" style={{ background: 'var(--panel)', borderColor: 'rgba(255,255,255,0.02)' }}>
          <p className="text-sm text-[var(--muted)]">
            <span className="font-semibold text-white">Current Step:</span> {jobStatus.current_step}
          </p>
        </div>
      )}

      {/* Download Button and Warning */}
      {jobStatus.status === 'COMPLETED' && jobStatus.output_video_url && (
        <>
          <div className="w-full bg-black rounded overflow-hidden">
            <video
              controls
              className="w-full max-h-96"
              src={jobStatus.output_video_url}
            >
              Your browser does not support the video tag.
            </video>
          </div>

          <a
            href={jobStatus.output_video_url}
            download
            className="block w-full mt-3 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg text-center transition"
          >
            ⬇️ Download Video
          </a>

          <div className="mt-4 bg-yellow-900 border border-yellow-700 text-yellow-100 px-4 py-3 rounded text-sm">
            ⚠️ <b>Important:</b> Your video will be deleted from our server after 1 hour. No upload history is kept. Please download and save your output now.
          </div>
        </>
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
