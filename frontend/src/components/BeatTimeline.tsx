import { useEffect, useRef, useState, useMemo } from 'react'

interface ProposedCut {
  time: number
  confidence?: number
}

interface BeatTimelineProps {
  musicFile: File
  beats?: number[]
  proposedCuts?: ProposedCut[]
  onSelectCut?: (time: number) => void
  onAcceptedCuts?: (cuts: number[]) => void
  regionStart?: number
  regionEnd?: number
  currentTime: number
  isPlaying: boolean
  onTogglePlay: () => void
  onSeek: (time: number) => void
  playPending?: boolean
}

export default function BeatTimeline({ 
  musicFile, 
  beats = [], 
  proposedCuts = [], 
  onSelectCut, 
  onAcceptedCuts, 
  regionStart = 0, 
  regionEnd,
  currentTime,
  isPlaying,
  onTogglePlay,
  onSeek
  , playPending = false
}: BeatTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null)
  const playheadCanvasRef = useRef<HTMLCanvasElement>(null)
  
  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null)
  const [waveReady, setWaveReady] = useState(false)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const previewSourceRef = useRef<AudioBufferSourceNode | null>(null)
  const previewTimeoutRef = useRef<number | null>(null)
  const [zoom] = useState<number>(1)
  const [snapToBeats, setSnapToBeats] = useState(true)
  const [acceptedCuts, setAcceptedCuts] = useState<Record<number, boolean>>({})
  const [hoverTime, setHoverTime] = useState<number | null>(null)
  const [hoverX, setHoverX] = useState<number | null>(null)
  const [hoverBeat, setHoverBeat] = useState<number | null>(null)

  // 1. Decode Audio Once
  useEffect(() => {
    let cancelled = false
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
    audioCtxRef.current = ctx

    async function decode() {
      try {
        const arrayBuffer = await musicFile.arrayBuffer()
        const decoded = await ctx.decodeAudioData(arrayBuffer)
        if (!cancelled) {
          setAudioBuffer(decoded)
          setWaveReady(true)
          // Suspend context to avoid blocking HTML audio element
          try { await ctx.suspend() } catch (e) {}
        }
      } catch (err) {
        console.error('Audio decode failed', err)
      }
    }

    decode()
    return () => { 
      cancelled = true
      stopPreview()
      try { ctx.close() } catch (e) {} 
      setWaveReady(false)
    }
  }, [musicFile])

  // 2. Pre-compute Peaks (Optimization)
  // We create a downsampled version of the waveform for fast rendering
  const peaks = useMemo(() => {
    if (!audioBuffer) return null
    const raw = audioBuffer.getChannelData(0)
    const samples = raw.length
    // Target ~20000 points for the whole file (enough for 4k screens)
    const step = Math.ceil(samples / 20000) 
    const data = new Float32Array(Math.ceil(samples / step) * 2)
    
    for (let i = 0, ptr = 0; i < samples; i += step) {
      let min = 1.0
      let max = -1.0
      for (let j = 0; j < step && i + j < samples; j++) {
        const v = raw[i + j]
        if (v < min) min = v
        if (v > max) max = v
      }
      data[ptr++] = min
      data[ptr++] = max
    }
    return { data, step, length: samples }
  }, [audioBuffer])

  // Helper to get view window
  const getViewWindow = () => {
    if (!audioBuffer) return { start: 0, end: 0 }
    
    if (regionEnd) {
      return { start: regionStart, end: regionEnd }
    }
    
    const viewSec = Math.max(5, audioBuffer.duration / zoom)
    const center = Math.min(Math.max(currentTime, viewSec / 2), Math.max(audioBuffer.duration - viewSec / 2, 0))
    const start = Math.max(0, center - viewSec / 2)
    const end = Math.min(audioBuffer.duration, start + viewSec)
    return { start, end }
  }

  // 3. Draw Waveform (Only when view changes significantly or data changes)
  useEffect(() => {
    if (!peaks || !waveformCanvasRef.current || !audioBuffer) return

    const canvas = waveformCanvasRef.current
    const dpr = window.devicePixelRatio || 1
    const width = canvas.clientWidth * dpr
    const height = canvas.clientHeight * dpr
    
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }

    const c = canvas.getContext('2d')
    if (!c) return

    // Clear
    c.fillStyle = '#0b0f14'
    c.fillRect(0, 0, width, height)

    // Grid
    c.strokeStyle = 'rgba(255, 255, 255, 0.05)'
    c.lineWidth = 1
    c.beginPath()
    for (let i = 0; i < width; i += 50 * dpr) {
      c.moveTo(i, 0)
      c.lineTo(i, height)
    }
    c.stroke()

    const { start: viewStart, end: viewEnd } = getViewWindow()
    const viewDuration = viewEnd - viewStart
    if (viewDuration <= 0) return

    // Draw Waveform using Peaks
    const amp = height / 2
    c.shadowBlur = 0
    c.strokeStyle = '#39FF7A'
    c.lineWidth = Math.max(1, dpr)
    c.beginPath()

    // Map pixel x to time, then to peak index
    const pixels = width
    const timePerPixel = viewDuration / pixels
    
    for (let x = 0; x < pixels; x++) {
      const t = viewStart + x * timePerPixel
      const sampleIdx = Math.floor(t * audioBuffer.sampleRate)
      const peakIdx = Math.floor(sampleIdx / peaks.step) * 2
      
      if (peakIdx >= 0 && peakIdx < peaks.data.length - 1) {
        const min = peaks.data[peakIdx]
        const max = peaks.data[peakIdx + 1]
        
        // Optimization: Skip flat lines
        if (Math.abs(min) < 0.01 && Math.abs(max) < 0.01) {
            c.moveTo(x, amp)
            c.lineTo(x, amp)
            continue
        }

        const y1 = (1 + min) * amp
        const y2 = (1 + max) * amp
        c.moveTo(x, y1)
        c.lineTo(x, y2)
      }
    }
    c.stroke()

    // Draw Beats
    // brighter, taller beat markers
    beats.forEach((b) => {
      if (b < viewStart || b > viewEnd) return
      const x = ((b - viewStart) / viewDuration) * width
      c.fillStyle = 'rgba(255, 209, 102, 0.9)'
      c.fillRect(x - 2, height * 0.05, 4, height * 0.9)
      // highlight small halo
      c.beginPath()
      c.arc(x, height * 0.5, 6 * dpr, 0, Math.PI * 2)
      c.fillStyle = 'rgba(255,209,102,0.06)'
      c.fill()
    })

    // Draw Cuts
    proposedCuts.forEach((p) => {
      if (p.time < viewStart || p.time > viewEnd) return
      const x = ((p.time - viewStart) / viewDuration) * width
      
      if (acceptedCuts[p.time]) {
        c.fillStyle = '#39FF7A'
        c.fillRect(x - 2, 0, 4, height)
      } else {
        c.fillStyle = p.confidence && p.confidence < 0.5 ? 'rgba(239, 68, 68, 0.5)' : 'rgba(255, 209, 102, 0.8)'
        c.fillRect(x - 1, height * 0.8, 2, height * 0.2)
      }
    })

    // Draw hover marker if present
    if (hoverTime !== null && hoverTime >= viewStart && hoverTime <= viewEnd && hoverX !== null) {
      const x = hoverX
      c.strokeStyle = 'rgba(255,255,255,0.2)'
      c.lineWidth = 1 * dpr
      c.beginPath()
      c.moveTo(x, 0)
      c.lineTo(x, height)
      c.stroke()
      c.fillStyle = 'rgba(255,255,255,0.06)'
      c.fillRect(x - 10, height * 0.02, 20, height * 0.12)
    }

  }, [peaks, beats, proposedCuts, zoom, regionStart, regionEnd, currentTime, acceptedCuts]) 
  // Note: We still depend on currentTime for scrolling, but using 'peaks' makes it fast (20k points vs 10M)

  // Play a short preview at a given time (used on hover)
  const stopPreview = () => {
    try {
      if (previewTimeoutRef.current) {
        clearTimeout(previewTimeoutRef.current)
        previewTimeoutRef.current = null
      }
      if (previewSourceRef.current) {
        previewSourceRef.current.stop()
        previewSourceRef.current.disconnect()
        previewSourceRef.current = null
      }
    } catch (e) {
      // ignore
    }
  }

  const playPreview = async (time: number, durationSec = 0.25) => {
    if (!audioBuffer || !audioCtxRef.current) return
    try {
      const ctx = audioCtxRef.current
      if (ctx.state === 'suspended') await ctx.resume()
      stopPreview()
      const src = ctx.createBufferSource()
      src.buffer = audioBuffer
      src.connect(ctx.destination)
      previewSourceRef.current = src
      src.start(0, Math.max(0, time - 0.02), durationSec)
      // schedule cleanup
      previewTimeoutRef.current = window.setTimeout(() => {
        stopPreview()
      }, durationSec * 1000 + 50)
    } catch (err) {
      console.error('Preview play failed', err)
      stopPreview()
    }
  }

  // 4. Draw Playhead (Separate Canvas)
  useEffect(() => {
    if (!playheadCanvasRef.current || !audioBuffer) return
    const canvas = playheadCanvasRef.current
    const dpr = window.devicePixelRatio || 1
    const width = canvas.clientWidth * dpr
    const height = canvas.clientHeight * dpr

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }

    const c = canvas.getContext('2d')
    if (!c) return

    c.clearRect(0, 0, width, height)

    const { start: viewStart, end: viewEnd } = getViewWindow()
    
    if (currentTime >= viewStart && currentTime <= viewEnd) {
      const x = ((currentTime - viewStart) / (viewEnd - viewStart)) * width
      c.strokeStyle = '#FF2A6D'
      c.lineWidth = 2 * dpr
      c.shadowBlur = 5
      c.shadowColor = '#FF2A6D'
      c.beginPath()
      c.moveTo(x, 0)
      c.lineTo(x, height)
      c.stroke()
    }
  }, [currentTime, regionStart, regionEnd, zoom, audioBuffer])

  const formatTime = (s: number) => {
    if (!isFinite(s) || s < 0) return '0:00'
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  const handleCanvasClick = (e: React.MouseEvent) => {
    const canvas = playheadCanvasRef.current // Click on top canvas
    if (!canvas || !audioBuffer) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const { start: viewStart, end: viewEnd } = getViewWindow()
    
    let time = viewStart + (x / rect.width) * (viewEnd - viewStart)
    
    if (snapToBeats && beats.length) {
      let nearest = beats[0]
      let best = Math.abs(time - nearest)
      for (let b of beats) {
        const d = Math.abs(time - b)
        if (d < best) {
          best = d
          nearest = b
        }
      }
      time = nearest
    }
    onSelectCut && onSelectCut(time)
  }

  // Hover handlers for showing time and preview
  const handleMouseMove = (e: React.MouseEvent) => {
    const canvas = playheadCanvasRef.current || waveformCanvasRef.current
    if (!canvas || !audioBuffer) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const { start: viewStart, end: viewEnd } = getViewWindow()
    const time = viewStart + (x / rect.width) * (viewEnd - viewStart)
    setHoverTime(time)
    setHoverX(x)

    // find nearest beat within 0.15s
    let nearest: number | null = null
    let best = 0.15
    for (let b of beats) {
      const d = Math.abs(time - b)
      if (d < best) {
        best = d
        nearest = b
      }
    }
    setHoverBeat(nearest)

    // Don't play preview during active playback or pending
    if (!isPlaying && !playPending) {
      // Debounce: cancel pending preview and schedule new one
      if (previewTimeoutRef.current) {
        clearTimeout(previewTimeoutRef.current)
      }
      previewTimeoutRef.current = window.setTimeout(() => {
        playPreview(time, 0.15)
      }, 150)
    }
  }

  const handleMouseLeave = () => {
    setHoverTime(null)
    setHoverX(null)
    setHoverBeat(null)
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current)
      previewTimeoutRef.current = null
    }
    stopPreview()
  }

  // Stop preview when main playback starts
  useEffect(() => {
    if (isPlaying) {
      stopPreview()
      // Ensure AudioContext is suspended to not interfere with HTML audio
      if (audioCtxRef.current && audioCtxRef.current.state === 'running') {
        audioCtxRef.current.suspend().catch(() => {})
      }
    }
  }, [isPlaying])


  const toggleAccept = (t: number) => {
    setAcceptedCuts((prev) => {
      const copy = { ...prev }
      if (copy[t]) delete copy[t]
      else copy[t] = true
      const accepted = Object.keys(copy).map((k) => Number(k)).sort((a, b) => a - b)
      onAcceptedCuts && onAcceptedCuts(accepted)
      return copy
    })
  }

  return (
    <div className="w-full min-h-[280px] flex flex-col gap-4" ref={containerRef}>
      {/* Main Canvas Area */}
      <div className="flex-1 relative group min-h-[200px] rounded-lg overflow-hidden border border-slate-800 bg-[#0b0f14]">
        {/* Layer 1: Waveform */}
        <canvas 
          ref={waveformCanvasRef} 
          className="absolute inset-0 w-full h-full block"
        />
        {/* Layer 2: Playhead & Interaction */}
        <canvas 
          ref={playheadCanvasRef}
          onClick={handleCanvasClick}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="absolute inset-0 w-full h-full block cursor-crosshair z-10"
        />

        {!waveReady && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm bg-black/50 backdrop-blur-sm z-20">
            <div className="flex items-center gap-2">
              <span className="animate-spin">*</span>
              <span>Loading waveform...</span>
            </div>
          </div>
        )}
        
        {/* Floating Controls */}
        <div className="absolute top-4 right-4 flex items-center gap-2 bg-black/60 backdrop-blur-md p-1.5 rounded-lg border border-neon-red/40 z-20">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              if (!playPending) onTogglePlay()
            }}
            disabled={playPending}
            className={`w-8 h-8 flex items-center justify-center rounded bg-neon-red/10 text-neon-red border border-neon-red/50 hover:bg-neon-red hover:text-black transition-all ${playPending ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {playPending ? '…' : (isPlaying ? '⏸' : '▶')}
          </button>
          <div className="h-4 w-px bg-white/10 mx-1"></div>
          <label className="text-[10px] uppercase tracking-widest text-slate-400 font-bold px-2 cursor-pointer select-none flex items-center gap-2">
            <span>Snap</span>
            <input 
              type="checkbox" 
              checked={snapToBeats} 
              onChange={(e) => setSnapToBeats(e.target.checked)}
              className="accent-neon-green w-3 h-3 rounded border-slate-600 bg-slate-800"
            />
          </label>
        </div>

        {/* Play Overlay */}
        {!isPlaying && (
          <div 
            onClick={(e) => { e.stopPropagation(); onTogglePlay() }}
            className="absolute inset-0 flex items-center justify-center cursor-pointer group/play z-20"
          >
            <div className="w-16 h-16 rounded-full bg-neon-red/10 border border-neon-red/50 flex items-center justify-center backdrop-blur-sm shadow-[0_0_40px_rgba(255,0,0,0.25)] animate-pulse group-hover/play:scale-110 transition-transform">
              <span className="text-3xl text-neon-red ml-1">▶</span>
            </div>
          </div>
        )}

        {/* Hover Tooltip */}
        {hoverTime !== null && hoverX !== null && (
          <div
            className="absolute z-30 pointer-events-none text-xs text-white bg-black/60 px-2 py-1 rounded-md backdrop-blur-md border border-white/10"
            style={{ left: Math.max(8, Math.min((hoverX as number) - 40, (waveformCanvasRef.current?.clientWidth || 800) - 80)), top: 8 }}
          >
            <div className="font-mono">{formatTime(hoverTime)}</div>
            {hoverBeat !== null && (
              <div className="text-[11px] text-neon-green">Beat detected</div>
            )}
          </div>
        )}
      </div>

      {/* Proposed Cuts Strip */}
      {proposedCuts.length > 0 && (
        <div className="h-10 flex items-center gap-2 overflow-x-auto custom-scrollbar pb-1 px-1">
          <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold whitespace-nowrap mr-2 sticky left-0 bg-[#080a0e] z-10 pr-2">
            Detected Cuts
          </div>
          {proposedCuts.map((p, i) => (
            <div
              key={i}
              className={`
                flex-shrink-0 flex items-center rounded border text-[10px] font-mono transition-all overflow-hidden
                ${acceptedCuts[p.time] 
                  ? 'bg-neon-green/20 border-neon-green text-neon-green shadow-[0_0_10px_rgba(57,255,122,0.2)]' 
                  : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'}
              `}
            >
              <button 
                type="button"
                onClick={() => onSeek(p.time)}
                className="px-2 py-1 hover:bg-white/10 border-r border-white/10"
                title="Jump to time"
              >
                {formatTime(p.time)}
              </button>
              <button 
                type="button"
                onClick={() => toggleAccept(p.time)}
                className="px-2 py-1 hover:bg-white/10 font-bold"
                title="Toggle Cut"
              >
                {acceptedCuts[p.time] ? '✓' : '+'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
