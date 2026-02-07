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
  zoom?: number
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
  onSeek: _onSeek,
  playPending = false,
  zoom = 1
}: BeatTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const waveformCanvasRef = useRef<HTMLCanvasElement>(null)
  const playheadCanvasRef = useRef<HTMLCanvasElement>(null)

  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null)
  const [waveReady, setWaveReady] = useState(false)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const previewSourceRef = useRef<AudioBufferSourceNode | null>(null)
  const previewTimeoutRef = useRef<number | null>(null)
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
          try { await ctx.suspend() } catch (e) { }
        }
      } catch (err) {
        console.error('Audio decode failed', err)
      }
    }

    decode()
    return () => {
      cancelled = true
      stopPreview()
      try { ctx.close() } catch (e) { }
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
      // Apply zoom to the selected region
      const regionDuration = regionEnd - regionStart
      const zoomedDuration = regionDuration / zoom
      const center = regionStart + regionDuration / 2
      const start = Math.max(regionStart, center - zoomedDuration / 2)
      const end = Math.min(regionEnd, center + zoomedDuration / 2)
      return { start, end }
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

    // Clear background
    c.fillStyle = '#05070a'
    c.fillRect(0, 0, width, height)

    // Center Zero-Crossing Line
    c.strokeStyle = 'rgba(255, 255, 255, 0.03)'
    c.beginPath()
    c.moveTo(0, height / 2)
    c.lineTo(width, height / 2)
    c.stroke()

    const { start: viewStart, end: viewEnd } = getViewWindow()
    const viewDuration = viewEnd - viewStart
    if (viewDuration <= 0) return

    // Draw Waveform using Peaks
    const amp = height / 2

    // Professional mirrored gradient
    const grad = c.createLinearGradient(0, height * 0.2, 0, height * 0.8)
    grad.addColorStop(0, '#00C2FF')
    grad.addColorStop(0.5, '#00F0FF')
    grad.addColorStop(1, '#00C2FF')

    c.strokeStyle = grad
    c.lineWidth = Math.max(1, dpr * 0.75)
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

        // Mirroring: ensure we draw from center out
        // Apply 0.8 scaling to leave some padding at top/bottom
        const y1 = amp + (min * amp * 0.85)
        const y2 = amp + (max * amp * 0.85)

        c.moveTo(x, y1)
        c.lineTo(x, y2)
      }
    }
    c.stroke()

    // Draw Beats - Professional Centered Look
    beats.forEach((b) => {
      if (b < viewStart || b > viewEnd) return
      const x = ((b - viewStart) / viewDuration) * width

      // Glow under the beat
      const beatGrad = c.createLinearGradient(x, 0, x, height)
      beatGrad.addColorStop(0, 'rgba(255, 0, 255, 0)')
      beatGrad.addColorStop(0.5, 'rgba(255, 0, 255, 0.4)')
      beatGrad.addColorStop(1, 'rgba(255, 0, 255, 0)')

      c.fillStyle = beatGrad
      c.fillRect(x - 4 * dpr, 0, 8 * dpr, height)

      // Core Beat line
      c.fillStyle = '#FF00FF'
      c.shadowBlur = 10
      c.shadowColor = 'rgba(255, 0, 255, 0.8)'
      c.fillRect(x - 1 * dpr, height * 0.1, 2 * dpr, height * 0.8)
      c.shadowBlur = 0
    })

    // Draw Cuts
    proposedCuts.forEach((p) => {
      if (p.time < viewStart || p.time > viewEnd) return
      const x = ((p.time - viewStart) / viewDuration) * width

      if (acceptedCuts[p.time]) {
        c.fillStyle = '#39FF7A'
        c.fillRect(x - 1.5 * dpr, 0, 3 * dpr, height)
      } else {
        c.fillStyle = p.confidence && p.confidence < 0.5 ? 'rgba(239, 68, 68, 0.5)' : 'rgba(255, 209, 102, 0.8)'
        c.fillRect(x - 0.5 * dpr, height * 0.8, 1 * dpr, height * 0.2)
      }
    })

    // Draw hover marker
    if (hoverTime !== null && hoverTime >= viewStart && hoverTime <= viewEnd && hoverX !== null) {
      const x = hoverX * dpr
      c.strokeStyle = 'rgba(255,255,255,0.4)'
      c.lineWidth = 1 * dpr
      c.setLineDash([4, 4])
      c.beginPath()
      c.moveTo(x, 0)
      c.lineTo(x, height)
      c.stroke()
      c.setLineDash([])
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
      c.strokeStyle = '#00F0FF'
      c.lineWidth = 3 * dpr
      c.shadowBlur = 10
      c.shadowColor = 'rgba(0, 240, 255, 0.8)'
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
        audioCtxRef.current.suspend().catch(() => { })
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
    <div className="w-full h-full flex flex-col" ref={containerRef}>
      {/* Main Canvas Area */}
      <div className="flex-1 relative group min-h-0 rounded-lg overflow-hidden border border-slate-800 bg-[#0b0f14]">
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

        {/* Floating Controls - Simplified */}
        <div className="absolute top-2 right-2 flex items-center gap-2 bg-black/70 backdrop-blur-md px-2 py-1 rounded-lg z-20 border border-white/10">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              if (!playPending) onTogglePlay()
            }}
            disabled={playPending}
            className="w-7 h-7 flex items-center justify-center rounded bg-reel/20 text-reel border border-reel/30 hover:bg-reel/30 transition-all disabled:opacity-50"
          >
            {playPending ? '…' : (isPlaying ? '⏸' : '▶')}
          </button>
          <label className="text-[9px] text-text-muted font-medium px-1 cursor-pointer select-none flex items-center gap-1.5">
            <span>Snap</span>
            <input
              type="checkbox"
              checked={snapToBeats}
              onChange={(e) => setSnapToBeats(e.target.checked)}
              className="accent-reel w-3 h-3"
            />
          </label>
        </div>

        {/* Center Play Button - Only when paused */}
        {!isPlaying && waveReady && (
          <div
            onClick={(e) => { e.stopPropagation(); onTogglePlay() }}
            className="absolute inset-0 flex items-center justify-center cursor-pointer group/play z-15"
          >
            <div className="w-12 h-12 rounded-full flex items-center justify-center bg-reel/20 border border-reel/40 hover:bg-reel/30 hover:scale-110 transition-all">
              <span className="text-xl ml-0.5 text-reel">▶</span>
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

      {/* Proposed Cuts Strip - Compact */}
      {proposedCuts.length > 0 && (
        <div className="h-8 shrink-0 flex items-center gap-1.5 overflow-x-auto custom-scrollbar px-1 bg-black/30 border-t border-white/5">
          <span className="text-[8px] uppercase text-text-muted font-bold whitespace-nowrap mr-1">Cuts:</span>
          {proposedCuts.map((p, i) => (
            <button
              key={i}
              onClick={() => toggleAccept(p.time)}
              className={`
                flex-shrink-0 px-2 py-0.5 rounded text-[9px] font-mono transition-all border
                ${acceptedCuts[p.time]
                  ? 'bg-reel/20 border-reel text-reel'
                  : 'bg-white/5 border-white/10 text-text-muted hover:border-white/30'}
              `}
            >
              {formatTime(p.time)} {acceptedCuts[p.time] ? '✓' : '+'}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
