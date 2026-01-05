import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import MusicTimeline from './MusicTimeline'
import BeatTimeline from './BeatTimeline'
import StyleSelector from './StyleSelector'

interface UploadFormProps {
  onJobCreated: (jobId: string) => void
  style: string
  onStyleChange: (style: string) => void
}

export default function UploadForm({ onJobCreated, style, onStyleChange }: UploadFormProps) {
  const [videos, setVideos] = useState<File[]>([])
  const [music, setMusic] = useState<File | null>(null)
  const [musicUrl, setMusicUrl] = useState<string | null>(null)
  const [musicStartTime, setMusicStartTime] = useState(0)
  const [musicEndTime, setMusicEndTime] = useState(30)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [beats, setBeats] = useState<number[]>([])
  const [proposedCuts, setProposedCuts] = useState<Array<{ time: number; confidence?: number }>>([])
  const [acceptedCuts, setAcceptedCuts] = useState<number[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  
  // Audio State (Centralized)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playPending, setPlayPending] = useState(false)

  // Stable object URL for audio element to avoid reloading on every render
  useEffect(() => {
    if (!music) {
      setMusicUrl(null)
      return
    }

    const url = URL.createObjectURL(music)
    setMusicUrl(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [music])

  // Initialize audio element when music changes
  useEffect(() => {
    if (!music || !audioRef.current) return
    
    console.log('Music file changed, initializing audio element...')
    
    // Reset states
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    
    return () => {
      // Cleanup: pause when component unmounts or music changes
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
      }
    }
  }, [music])

  // Auto-analyze beats when region changes
  useEffect(() => {
    if (!music) return
    
    const timer = setTimeout(async () => {
      setAnalyzing(true)
      try {
        const fd = new FormData()
        fd.append('audio', music)
        const query = `?start=${musicStartTime}&end=${musicEndTime}`
        const resp = await fetch('/api/analyze-beats' + query, { method: 'POST', body: fd })
        if (!resp.ok) throw new Error('Analysis failed')
        const data = await resp.json()
        setBeats(data.beats || [])
        setProposedCuts(data.proposedCuts || [])
      } catch (err) {
        console.error(err)
      } finally {
        setAnalyzing(false)
      }
    }, 800) // 800ms debounce to allow dragging

    return () => clearTimeout(timer)
  }, [music, musicStartTime, musicEndTime])

  // Audio Handlers
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const t = audioRef.current.currentTime
      setCurrentTime(t)
      
      // Loop region logic
      if (isPlaying && (t < musicStartTime || t >= musicEndTime)) {
        audioRef.current.currentTime = musicStartTime
      }
    }
  }

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      const dur = audioRef.current.duration
      setDuration(dur)
      audioRef.current.volume = 1.0
      audioRef.current.muted = false
      console.log('Audio loaded:', { 
        duration: dur, 
        readyState: audioRef.current.readyState, 
        volume: audioRef.current.volume,
        muted: audioRef.current.muted,
        paused: audioRef.current.paused,
        src: audioRef.current.src?.substring(0, 50) 
      })
    }
  }

  const togglePlay = async () => {
    if (!audioRef.current || playPending) return
    console.log('togglePlay called', { 
      isPlaying, 
      readyState: audioRef.current.readyState, 
      currentTime: audioRef.current.currentTime,
      volume: audioRef.current.volume,
      muted: audioRef.current.muted
    })
    setPlayPending(true)
    try {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
        console.log('Audio paused')
      } else {
        if (currentTime < musicStartTime || currentTime >= musicEndTime) {
          audioRef.current.currentTime = musicStartTime
        }
        // Ensure not muted
        audioRef.current.muted = false
        audioRef.current.volume = 1.0
        // Await play() promise to avoid race conditions
        console.log('Attempting to play audio...')
        await audioRef.current.play()
        setIsPlaying(true)
        console.log('Audio playing successfully', {
          paused: audioRef.current.paused,
          volume: audioRef.current.volume,
          muted: audioRef.current.muted,
          currentTime: audioRef.current.currentTime
        })
      }
    } catch (err) {
      console.error('Playback error:', err)
      setIsPlaying(false)
    } finally {
      setPlayPending(false)
    }
  }

  const seek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  // Refs for file inputs to trigger them programmatically if needed
  const videoInputRef = useRef<HTMLInputElement>(null)
  const musicInputRef = useRef<HTMLInputElement>(null)

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
      if (acceptedCuts && acceptedCuts.length) {
        formData.append('accepted_cuts', JSON.stringify(acceptedCuts))
      }

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      onJobCreated(response.data.job_id)
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
    <form onSubmit={handleSubmit} className="h-full flex flex-col bg-[#0b0f14]">
      {/* Central Audio Element */}
      {musicUrl && (
        <audio
          ref={audioRef}
          src={musicUrl}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
          onError={(e) => console.error('Audio element error:', e)}
          preload="auto"
          className="hidden"
        />
      )}
      
      {/* Top Workspace (Assets & Style) */}
      <div className="flex-1 p-6 overflow-y-auto custom-scrollbar">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          
          {/* Column 1: Video Assets */}
          <div className="flex flex-col gap-6 h-full">
            <div className="bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-2xl p-6 flex-1 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <label className="text-neon-blue font-mono text-xs tracking-widest uppercase flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-neon-blue shadow-[0_0_10px_rgba(0,240,255,0.5)]"></span>
                  Source Footage
                </label>
                <span className="text-[10px] text-slate-500 font-mono border border-slate-800 px-2 py-0.5 rounded">MP4/MOV</span>
              </div>
              
              <div 
                className={`relative flex-1 border-2 border-dashed rounded-xl transition-all duration-300 group flex flex-col items-center justify-center
                  ${videos.length > 0 ? 'border-neon-blue/30 bg-neon-blue/5' : 'border-slate-800 hover:border-slate-600 hover:bg-slate-800/30'}
                `}
              >
                <input
                  ref={videoInputRef}
                  type="file"
                  multiple
                  accept="video/*"
                  onChange={handleVideoChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="text-center pointer-events-none p-4">
                  <div className={`text-3xl mb-3 transition-transform duration-300 ${videos.length > 0 ? 'scale-110' : 'group-hover:scale-110'}`}>
                    {videos.length > 0 ? '📼' : '📹'}
                  </div>
                  <p className="text-slate-300 font-medium text-sm">
                    {videos.length > 0 ? `${videos.length} Clips Ready` : 'Drop footage'}
                  </p>
                </div>
              </div>

              {videos.length > 0 && (
                <div className="bg-black/40 rounded-lg border border-white/5 p-2 max-h-32 overflow-y-auto custom-scrollbar">
                  <ul className="space-y-1">
                    {videos.map((v, i) => (
                      <li key={i} className="text-[10px] text-slate-400 font-mono flex items-center truncate">
                        <span className="text-neon-blue mr-2">►</span> {v.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Column 2: Audio Assets */}
          <div className="flex flex-col gap-6 h-full">
            <div className="bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-2xl p-6 flex-1 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <label className="text-neon-purple font-mono text-xs tracking-widest uppercase flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-neon-purple shadow-[0_0_10px_rgba(176,38,255,0.5)]"></span>
                  Audio Track
                </label>
                <span className="text-[10px] text-slate-500 font-mono border border-slate-800 px-2 py-0.5 rounded">MP3/WAV</span>
              </div>

              <div 
                className={`relative flex-1 border-2 border-dashed rounded-xl transition-all duration-300 group flex flex-col items-center justify-center
                  ${music ? 'border-neon-purple/30 bg-neon-purple/5' : 'border-slate-800 hover:border-slate-600 hover:bg-slate-800/30'}
                `}
              >
                <input
                  ref={musicInputRef}
                  type="file"
                  accept="audio/*"
                  onChange={handleMusicChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="text-center pointer-events-none p-4">
                  <div className={`text-3xl mb-3 transition-transform duration-300 ${music ? 'scale-110' : 'group-hover:scale-110'}`}>
                    {music ? '🎵' : '🎧'}
                  </div>
                  <p className="text-slate-300 font-medium text-sm truncate max-w-[200px]">
                    {music ? music.name : 'Drop audio'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Column 3: Creative Direction */}
          <div className="bg-slate-900/40 backdrop-blur-md border border-white/5 rounded-2xl p-8 flex flex-col h-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-3">
                <span className="text-2xl">🎨</span> Creative Direction
              </h2>
              <div className="text-xs font-mono text-slate-500">
                SELECT STYLE PRESET
              </div>
            </div>
            
            <div className="flex-1">
              <StyleSelector selectedStyle={style} onStyleChange={onStyleChange} />
            </div>

            {/* Submit Action - Floating at bottom right of this panel */}
            <div className="mt-8 pt-6 border-t border-white/5 flex justify-end items-center gap-4">
              {error && (
                <div className="text-red-400 text-xs font-mono bg-red-500/10 px-3 py-2 rounded border border-red-500/20">
                  ⚠️ {error}
                </div>
              )}
              <button
                type="submit"
                disabled={loading || videos.length === 0 || !music}
                className={`
                  px-8 py-4 rounded-xl font-bold text-sm tracking-widest uppercase transition-all duration-300 flex items-center gap-3
                  ${loading || videos.length === 0 || !music 
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                    : 'bg-neon-green text-black hover:shadow-[0_0_30px_rgba(57,255,122,0.4)] hover:scale-[1.02]'}
                `}
              >
                {loading ? (
                  <>
                    <span className="animate-spin">⚙️</span> Rendering...
                  </>
                ) : (
                  <>
                    🚀 Initialize Render
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Panel: Audio Workbench */}
      <div className="h-[380px] bg-[#080a0e] border-t border-white/5 flex flex-col relative z-20 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
        {music ? (
          <div className="flex-1 flex flex-col">
            {/* Workbench Header */}
            <div className="h-12 border-b border-white/5 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-sm">
              <div className="flex items-center gap-4">
                <label className="text-neon-green font-mono text-xs tracking-widest uppercase flex items-center gap-2">
                  <span className="animate-pulse w-2 h-2 rounded-full bg-neon-green shadow-[0_0_10px_rgba(57,255,122,0.5)]"></span>
                  Audio Intelligence Workbench
                </label>
                <div className="h-4 w-px bg-white/10"></div>
                <span className="text-xs font-mono text-slate-400">
                  {musicStartTime.toFixed(1)}s - {musicEndTime.toFixed(1)}s SELECTED
                </span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={togglePlay}
                  disabled={playPending}
                  className={`
                    w-8 h-8 flex items-center justify-center rounded-full border transition-all
                      ${isPlaying 
                        ? 'border-neon-green text-neon-green bg-neon-green/10 shadow-[0_0_10px_rgba(57,255,122,0.3)]' 
                        : 'border-slate-500 text-slate-400 hover:border-neon-green hover:text-neon-green'}
                  `}
                >
                    {playPending ? '…' : (isPlaying ? '⏸' : '▶')}
                </button>

                <button
                  type="button"
                  onClick={async () => {
                    setAnalyzing(true)
                    try {
                      const fd = new FormData()
                      fd.append('audio', music)
                      const query = `?start=${musicStartTime}&end=${musicEndTime}`
                      const resp = await fetch('/api/analyze-beats' + query, { method: 'POST', body: fd })
                      if (!resp.ok) throw new Error('Analysis failed')
                      const data = await resp.json()
                      setBeats(data.beats || [])
                      setProposedCuts(data.proposedCuts || [])
                    } catch (err) {
                      setError(err instanceof Error ? err.message : 'Beat analysis failed')
                    } finally {
                      setAnalyzing(false)
                    }
                  }}
                  disabled={analyzing}
                  className="px-4 py-1.5 rounded bg-neon-green/10 text-neon-green border border-neon-green/30 hover:bg-neon-green/20 text-[10px] font-mono uppercase tracking-wider transition-all flex items-center gap-2"
                >
                  {analyzing ? <span className="animate-spin">⚡</span> : <span>🔎</span>}
                  {analyzing ? 'Processing...' : 'Analyze Region'}
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setBeats([])
                    setProposedCuts([])
                  }}
                  className="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 text-[10px] font-mono uppercase transition-colors"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Workbench Content */}
            <div className="flex-1 flex overflow-hidden">
              {/* Main Editor Area */}
              <div className="flex-1 p-6 flex flex-col gap-4 relative">
                {/* Region Navigator (Top Strip) */}
                <div className="h-16 bg-black/40 rounded-lg border border-white/5 relative overflow-hidden">
                   <MusicTimeline 
                    musicFile={music} 
                    onTimeSelect={handleTimeSelect}
                    currentTime={currentTime}
                    duration={duration}
                    isPlaying={isPlaying}
                    onTogglePlay={togglePlay}
                    onSeek={seek}
                    startTime={musicStartTime}
                    endTime={musicEndTime}
                  />
                </div>

                {/* Main Waveform (Bottom Large) */}
                <div className="flex-1 bg-black/40 rounded-xl border border-white/5 relative overflow-hidden p-4">
                  <BeatTimeline
                    musicFile={music}
                    beats={beats}
                    proposedCuts={proposedCuts}
                    currentTime={currentTime}
                    isPlaying={isPlaying}
                    onTogglePlay={togglePlay}
                    onSeek={seek}
                    regionStart={musicStartTime}
                    regionEnd={musicEndTime}
                    onSelectCut={(t) => seek(t)}
                    onAcceptedCuts={(cuts) => setAcceptedCuts(cuts)}
                    playPending={playPending}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-600 font-mono text-sm">
            <div className="text-center">
              <div className="text-4xl mb-4 opacity-20">🎹</div>
              <p>UPLOAD AUDIO TO ACTIVATE WORKBENCH</p>
            </div>
          </div>
        )}
      </div>
    </form>
  )
}
