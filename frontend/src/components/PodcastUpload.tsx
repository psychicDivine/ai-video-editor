import { useState, useEffect } from 'react'
import axios from 'axios'
import { Youtube, Upload, CheckCircle2, AlertCircle, Sparkles, Clock, User, Eye, Loader2 } from 'lucide-react'
import CaptionStyleSelector from './CaptionStyleSelector'

interface PodcastUploadProps {
  onJobCreated: (jobId: string) => void
}

interface YouTubeInfo {
  title: string
  thumbnail: string
  duration: number
  uploader: string
  view_count: number
  url: string
}

export default function PodcastUpload({ onJobCreated }: PodcastUploadProps) {
  const [tab, setTab] = useState<'upload' | 'youtube'>('upload')
  const [title, setTitle] = useState('')
  const [audio, setAudio] = useState<File | null>(null)
  const [video, setVideo] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [ytInfo, setYtInfo] = useState<YouTubeInfo | null>(null)
  const [fetchingInfo, setFetchingInfo] = useState(false)
  const [smartReels, setSmartReels] = useState(true)
  const [captionStyle, setCaptionStyle] = useState('tiktok')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Auto-fetch YouTube info when URL is pasted
  useEffect(() => {
    const fetchInfo = async () => {
      if (youtubeUrl.includes('youtube.com/') || youtubeUrl.includes('youtu.be/')) {
        setFetchingInfo(true)
        setError(null)
        try {
          const resp = await axios.post('/api/youtube/info', { url: youtubeUrl })
          setYtInfo(resp.data)
        } catch (err) {
          console.error('Failed to fetch YouTube info', err)
          setYtInfo(null)
        } finally {
          setFetchingInfo(false)
        }
      } else {
        setYtInfo(null)
      }
    }

    const timer = setTimeout(fetchInfo, 800)
    return () => clearTimeout(timer)
  }, [youtubeUrl])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (tab === 'youtube') {
        if (!youtubeUrl) throw new Error('Please enter a YouTube URL')
        const resp = await axios.post('/api/youtube/download', {
          url: youtubeUrl,
          enable_smart_reels: smartReels,
          caption_style: captionStyle
        })
        onJobCreated(resp.data.job_id)
      } else {
        if (!audio) throw new Error('Please select an audio file')
        const formData = new FormData()
        formData.append('audio', audio)
        if (video) formData.append('video', video)
        formData.append('title', title)
        formData.append('enable_smart_reels', String(smartReels))
        formData.append('caption_style', captionStyle)

        const resp = await axios.post('/api/podcast', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        onJobCreated(resp.data.job_id)
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const data = err.response?.data as any
        setError(data?.detail || data?.message || err.message)
      } else {
        setError(err instanceof Error ? err.message : 'Action failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      {/* Tab Switcher */}
      <div className="flex p-1 bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl mb-6 shadow-2xl">
        <button
          onClick={() => setTab('upload')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${tab === 'upload' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
            }`}
        >
          <Upload size={16} />
          Upload Files
        </button>
        <button
          onClick={() => setTab('youtube')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${tab === 'youtube' ? 'bg-red-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
            }`}
        >
          <Youtube size={16} />
          YouTube Link
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {tab === 'upload' ? (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Podcast Title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="How to build an AI SaaS..."
                className="w-full px-4 py-3 rounded-xl bg-slate-800/50 text-white border border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="relative group">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Audio (MP3/WAV)</label>
                <div className="relative border-2 border-dashed border-slate-700 group-hover:border-indigo-500/50 rounded-xl p-4 transition-all bg-slate-800/30 overflow-hidden">
                  <input type="file" accept="audio/*" onChange={(e) => e.target.files && setAudio(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                  <div className="text-center">
                    {audio ? (
                      <div className="flex flex-col items-center">
                        <CheckCircle2 size={24} className="text-green-500 mb-1" />
                        <span className="text-[10px] text-slate-300 truncate w-full px-2">{audio.name}</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center opacity-60 group-hover:opacity-100 transition-opacity">
                        <Upload size={20} className="text-slate-400 mb-1" />
                        <span className="text-[10px] text-slate-400 font-medium">Select Audio</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="relative group">
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Video (Optional)</label>
                <div className="relative border-2 border-dashed border-slate-700 group-hover:border-indigo-500/50 rounded-xl p-4 transition-all bg-slate-800/30 overflow-hidden">
                  <input type="file" accept="video/*" onChange={(e) => e.target.files && setVideo(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                  <div className="text-center">
                    {video ? (
                      <div className="flex flex-col items-center">
                        <CheckCircle2 size={24} className="text-green-500 mb-1" />
                        <span className="text-[10px] text-slate-300 truncate w-full px-2">{video.name}</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center opacity-60 group-hover:opacity-100 transition-opacity">
                        <Upload size={20} className="text-slate-400 mb-1" />
                        <span className="text-[10px] text-slate-400 font-medium">Select Video</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">YouTube URL</label>
              <div className="relative">
                <input
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-slate-800/50 text-white border border-slate-700 focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all outline-none"
                />
                <Youtube size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                {fetchingInfo && <Loader2 size={18} className="absolute right-4 top-1/2 -translate-y-1/2 text-red-500 animate-spin" />}
              </div>
            </div>

            {ytInfo && (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="flex gap-4 p-4">
                  <img src={ytInfo.thumbnail} className="w-32 aspect-video object-cover rounded-lg shadow-lg" alt="thumbnail" />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-bold text-white truncate mb-1">{ytInfo.title}</h3>
                    <div className="flex items-center gap-3 text-[10px] text-slate-400">
                      <span className="flex items-center gap-1"><User size={12} /> {ytInfo.uploader}</span>
                      <span className="flex items-center gap-1"><Clock size={12} /> {formatDuration(ytInfo.duration)}</span>
                      <span className="flex items-center gap-1"><Eye size={12} /> {(ytInfo.view_count / 1000).toFixed(1)}K</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* AI Features Toggle */}
        <div className="relative p-4 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 shadow-inner group overflow-hidden">
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
                <Sparkles size={18} className="animate-pulse" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  Generate Viral Clips
                  <span className="text-[10px] bg-indigo-500 text-white px-1.5 py-0.5 rounded uppercase tracking-tighter">AI</span>
                </h4>
                <p className="text-[10px] text-slate-400 mt-0.5">Auto-find, Smart Crop (9:16), & Enhance Vocal Clarity</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked={smartReels} onChange={(e) => setSmartReels(e.target.checked)} className="sr-only peer" />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-600/5 blur-3xl -z-0 group-hover:bg-indigo-600/10 transition-colors"></div>
        </div>

        {/* Caption Style Options */}
        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
          <details className="group open:pb-4">
            <summary className="list-none flex items-center justify-between cursor-pointer p-4 rounded-xl bg-slate-900/40 hover:bg-slate-900/60 transition-colors border border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-pink-500/20 rounded-lg text-pink-400">
                  <span className="text-lg">🎨</span>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">Caption Style</h4>
                  <p className="text-[10px] text-slate-400">Choose your subtitle visualization</p>
                </div>
              </div>
              <div className="text-slate-500 group-open:rotate-180 transition-transform">▼</div>
            </summary>
            <div className="pt-4 px-2">
              <CaptionStyleSelector
                selectedStyle={captionStyle}
                onStyleChange={setCaptionStyle}
              />
            </div>
          </details>
        </div>

        {error && (
          <div className="flex items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 text-red-100 rounded-xl animate-in shake duration-200">
            <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
            <p className="text-xs font-medium">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || (tab === 'upload' && !audio) || (tab === 'youtube' && !youtubeUrl)}
          className={`w-full relative py-4 rounded-xl font-black text-xs uppercase tracking-widest transition-all overflow-hidden ${loading
            ? 'bg-slate-800 text-slate-500 cursor-not-allowed shadow-none'
            : tab === 'upload'
              ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_20px_rgba(79,70,229,0.4)] active:scale-[0.98]'
              : 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)] active:scale-[0.98]'
            }`}
        >
          {loading ? (
            <div className="flex items-center justify-center gap-3">
              <Loader2 className="animate-spin" size={16} />
              <span>Analyzing Pipeline...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <Sparkles size={16} />
              <span>{tab === 'upload' ? 'Ignite Processing' : 'Direct Link Ignite'}</span>
            </div>
          )}
        </button>
      </form>
    </div>
  )
}
