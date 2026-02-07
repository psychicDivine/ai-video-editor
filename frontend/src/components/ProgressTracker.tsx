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
  preview_video_url?: string | null
}

export default function ProgressTracker({ jobId, onComplete }: ProgressTrackerProps) {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [_retryCount, setRetryCount] = useState(0)
  const cancelRef = useRef<Canceler | null>(null)

  useEffect(() => {
    let mounted = true
    let backoff = 1000

    const pollStatus = async () => {
      if (!mounted) return

      try {
        const source = axios.CancelToken.source()
        cancelRef.current = source.cancel

        const response = await axios.get(`/api/jobs/${jobId}`, {
          cancelToken: source.token,
          params: { _t: Date.now() }
        })

        if (!mounted) return

        setJobStatus(response.data)
        setLoading(false)
        setError(null)
        backoff = 1000 // Reset backoff on success

        if (response.data.status === 'COMPLETED') {
          onComplete()
          return
        } else if (response.data.status === 'FAILED') {
          setError(response.data.error_message || 'Processing failed')
          return
        }

        setTimeout(pollStatus, 3000)
      } catch (err) {
        if (axios.isCancel(err)) return
        if (!mounted) return

        const axiosError = err as AxiosError
        const msg = (axiosError.response?.data as any)?.detail || axiosError.message || 'Failed to fetch status'
        setError(msg)
        setLoading(false)

        const nextRetry = Math.min(backoff * 1.5, 10000)
        backoff = nextRetry
        setTimeout(pollStatus, nextRetry)
      }
    }

    pollStatus()

    return () => {
      mounted = false
      if (cancelRef.current) cancelRef.current()
    }
  }, [jobId, onComplete])

  if (loading && !jobStatus) {
    return (
      <div className="text-center text-slate-400 py-8">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-2 w-32 bg-slate-800 rounded-full mb-2"></div>
          <p className="text-xs">Initializing secure connection...</p>
        </div>
      </div>
    )
  }

  if (error && !jobStatus) {
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
        <div className="flex items-center gap-3 text-red-400 mb-3">
          <div className="font-bold text-sm">Connection Error</div>
        </div>
        <p className="text-xs text-red-200/60 mb-4">{error}</p>
        <button
          onClick={() => {
            setError(null)
            setLoading(true)
            setRetryCount(c => c + 1)
          }}
          className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-lg transition-all"
        >
          Re-establish Link
        </button>
      </div>
    )
  }

  if (!jobStatus) return null

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 block mb-1">Process Status</span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full animate-ping ${jobStatus.status === 'COMPLETED' ? 'bg-green-500' : 'bg-indigo-500'}`}></div>
            <span className="text-xs font-bold text-white">{jobStatus.status}</span>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 block mb-1">Efficiency</span>
          <span className="text-xs font-bold text-indigo-400">{jobStatus.progress}%</span>
        </div>
      </div>

      <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden shadow-inner">
        <div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-indigo-600 to-purple-600 transition-all duration-1000 ease-out"
          style={{ width: `${jobStatus.progress}%` }}
        >
          <div className="absolute inset-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.15)_50%,rgba(255,255,255,0.15)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem] animate-[move-bg_1s_linear_infinite]"></div>
        </div>
      </div>

      {jobStatus.current_step && (
        <div className="bg-slate-900/50 border border-slate-800 p-3 rounded-xl">
          <div className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter mb-1">Active Pipeline Step</div>
          <p className="text-[11px] text-slate-300 font-medium italic">"{jobStatus.current_step}"</p>
        </div>
      )}

      {jobStatus.status === 'COMPLETED' && jobStatus.output_video_url && (
        <div className="space-y-4 pt-2">
          {/* Show preview if available, otherwise try output_video_url */}
          {(jobStatus.preview_video_url || jobStatus.output_video_url.endsWith('.mp4')) && (
            <div className="aspect-video bg-black rounded-2xl overflow-hidden border border-slate-800 shadow-2xl relative">
              <video
                controls
                className="w-full h-full"
                src={jobStatus.preview_video_url || jobStatus.output_video_url}
                key={jobStatus.preview_video_url} // Force reload on url change
              />
            </div>
          )}

          {/* Quick Caption Restyle */}
          <div className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-xs font-bold text-white">Quick Restyle</h4>
                <p className="text-[10px] text-slate-400">Not happy? Change caption style instantly.</p>
              </div>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded">Preview Mode</span>
            </div>

            <div className="flex gap-2 overflow-x-auto pb-2">
              {['classic', 'tiktok', 'hormozi', 'neon'].map(style => (
                <button
                  key={style}
                  onClick={async () => {
                    setLoading(true); // Minimal loading state
                    try {
                      const res = await axios.post(`/api/captions/restyle/${jobId}`, { style });
                      // Update status with new preview
                      setJobStatus(prev => prev ? {
                        ...prev,
                        preview_video_url: `${res.data.preview_url}?t=${Date.now()}`
                      } : null);
                    } catch (err) {
                      console.error(err);
                      alert("Restyle failed");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="px-3 py-2 bg-slate-800 hover:bg-indigo-600 hover:text-white text-slate-300 text-[10px] font-bold uppercase rounded-lg transition-colors whitespace-nowrap"
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Download button - always use output_video_url */}
          <a
            href={jobStatus.output_video_url}
            download
            className="flex items-center justify-center gap-2 w-full py-4 bg-green-600 hover:bg-green-500 text-white rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-[0_0_20px_rgba(22,163,74,0.3)]"
          >
            {jobStatus.output_video_url.includes('/zip/') ? '📦 Download All Reels (ZIP)' : '⬇️ Retrieve Processed Output'}
          </a>
        </div>
      )}
    </div>
  )
}
