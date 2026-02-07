import React, { useEffect, useMemo, useRef, useState } from 'react'

interface MusicTimelineProps {
  musicFile: File
  onTimeSelect: (startTime: number, endTime: number) => void
  currentTime: number
  duration: number
  isPlaying: boolean
  onTogglePlay: () => void
  onSeek: (time: number) => void
  startTime: number
  endTime: number
}

export default function MusicTimeline({
  musicFile: _musicFile,
  onTimeSelect,
  currentTime,
  duration,
  isPlaying: _isPlaying,
  onTogglePlay: _onTogglePlay,
  onSeek,
  startTime,
  endTime
}: MusicTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null)
  const [dragMode, setDragMode] = useState<'move' | 'start' | 'end' | null>(null)
  const [dragOrigin, setDragOrigin] = useState<{ x: number; start: number; end: number } | null>(null)
  const totalDuration = Math.max(duration || 0, audioBuffer?.duration || 0, 1)
  const minWindow = Math.min(5, Math.max(1, totalDuration)) // seconds

  // Decode audio for mini-map peaks
  useEffect(() => {
    if (!_musicFile) return
    let cancelled = false
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()

    async function decode() {
      try {
        const buf = await _musicFile.arrayBuffer()
        const decoded = await ctx.decodeAudioData(buf)
        if (!cancelled) setAudioBuffer(decoded)
      } catch (err) {
        console.error('Mini-map decode failed', err)
      }
    }

    decode()
    return () => {
      cancelled = true
      try { ctx.close() } catch (e) { }
    }
  }, [_musicFile])

  const peaks = useMemo(() => {
    if (!audioBuffer) return null
    const channel = audioBuffer.getChannelData(0)
    const samples = channel.length
    const target = 2000
    const step = Math.max(1, Math.floor(samples / target))
    const out = new Float32Array(Math.ceil(samples / step) * 2)
    for (let i = 0, p = 0; i < samples; i += step) {
      let min = 1.0
      let max = -1.0
      for (let j = 0; j < step && i + j < samples; j++) {
        const v = channel[i + j]
        if (v < min) min = v
        if (v > max) max = v
      }
      out[p++] = min
      out[p++] = max
    }
    return { data: out, step, length: samples }
  }, [audioBuffer])

  // Ensure start/end always fit within the available duration
  useEffect(() => {
    const { start, end } = clampWindow(startTime, endTime)
    if (start !== startTime || end !== endTime) {
      onTimeSelect(start, end)
    }
  }, [totalDuration, startTime, endTime, onTimeSelect])

  const clampWindow = (start: number, end: number) => {
    const safeStart = Math.max(0, Math.min(start, totalDuration - minWindow))
    const safeEnd = Math.max(safeStart + minWindow, Math.min(end, totalDuration))
    return { start: safeStart, end: safeEnd }
  }

  const beginDrag = (mode: 'move' | 'start' | 'end') => (e: React.MouseEvent) => {
    e.preventDefault()
    setDragMode(mode)
    setDragOrigin({ x: e.clientX, start: startTime, end: endTime })
  }

  useEffect(() => {
    if (!dragMode || !dragOrigin) return

    const handleMove = (e: MouseEvent) => {
      if (!containerRef.current) return
      const rect = containerRef.current.getBoundingClientRect()
      const pxPerSec = rect.width / totalDuration
      const deltaSec = (e.clientX - dragOrigin.x) / pxPerSec

      if (dragMode === 'move') {
        const nextStart = dragOrigin.start + deltaSec
        const nextEnd = dragOrigin.end + deltaSec
        const { start, end } = clampWindow(nextStart, nextEnd)
        onTimeSelect(start, end)
        onSeek(start)
      }
      if (dragMode === 'start') {
        const nextStart = Math.min(dragOrigin.end - minWindow, dragOrigin.start + deltaSec)
        const { start, end } = clampWindow(nextStart, dragOrigin.end)
        onTimeSelect(start, end)
        onSeek(start)
      }
      if (dragMode === 'end') {
        const nextEnd = Math.max(dragOrigin.start + minWindow, dragOrigin.end + deltaSec)
        const { start, end } = clampWindow(dragOrigin.start, nextEnd)
        onTimeSelect(start, end)
      }
    }

    const handleUp = () => {
      setDragMode(null)
      setDragOrigin(null)
    }

    window.addEventListener('mousemove', handleMove)
    window.addEventListener('mouseup', handleUp)
    return () => {
      window.removeEventListener('mousemove', handleMove)
      window.removeEventListener('mouseup', handleUp)
    }
  }, [dragMode, dragOrigin, totalDuration, minWindow, onSeek, onTimeSelect])

  // Draw mini waveform background
  useEffect(() => {
    if (!canvasRef.current || !peaks || !totalDuration) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1
    const width = canvas.clientWidth * dpr
    const height = canvas.clientHeight * dpr
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width
      canvas.height = height
    }

    ctx.clearRect(0, 0, width, height)
    ctx.fillStyle = '#05070a' // Use canvas background
    ctx.fillRect(0, 0, width, height)

    const amp = height / 2
    const step = peaks.data.length / 2
    const pixels = width
    const samplesPerPixel = step / pixels

    // Professional mirrored gradient
    const grad = ctx.createLinearGradient(0, 0, 0, height)
    grad.addColorStop(0, '#00C2FF')
    grad.addColorStop(0.5, '#00F0FF')
    grad.addColorStop(1, '#00C2FF')

    ctx.strokeStyle = grad
    ctx.lineWidth = Math.max(1, dpr * 0.75)
    ctx.beginPath()
    for (let x = 0; x < pixels; x++) {
      const i = Math.floor(x * samplesPerPixel) * 2
      const min = peaks.data[i] || 0
      const max = peaks.data[i + 1] || 0

      // Mirroring: Draw from center (amp) outwards to min/max
      // min is negative (bottom), max is positive (top)
      // Actually standard peaks are usually both positive/negative relative to zero
      const y1 = amp + (min * amp * 0.8)
      const y2 = amp + (max * amp * 0.8)

      ctx.moveTo(x, y1)
      ctx.lineTo(x, y2)
    }
    ctx.stroke()
  }, [peaks, totalDuration])

  const regionLeftPct = (startTime / totalDuration) * 100
  const regionWidthPct = ((endTime - startTime) / totalDuration) * 100
  const playheadPct = (currentTime / totalDuration) * 100

  return (
    <div className="w-full h-full relative bg-[#0a0c10] overflow-hidden" ref={containerRef}>
      {/* Waveform Canvas */}
      <div className="absolute inset-0">
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />

        {/* Region selection indicator */}
        <div
          className="absolute inset-y-0 group/selection"
          style={{
            left: `${regionLeftPct}%`,
            width: `${regionWidthPct}%`,
          }}
        >
          {/* Core Box */}
          <div className="absolute inset-0 bg-reel/15 border-x-2 border-reel/60 cursor-grab active:cursor-grabbing" onMouseDown={beginDrag('move')} />

          {/* LEFT HANDLE */}
          <div
            className="absolute inset-y-0 -left-2 w-4 cursor-ew-resize flex items-center justify-center z-30"
            onMouseDown={beginDrag('start')}
          >
            <div className="w-1 h-8 bg-reel rounded-full" />
          </div>

          {/* RIGHT HANDLE */}
          <div
            className="absolute inset-y-0 -right-2 w-4 cursor-ew-resize flex items-center justify-center z-30"
            onMouseDown={beginDrag('end')}
          >
            <div className="w-1 h-8 bg-reel rounded-full" />
          </div>
        </div>

        {/* Playhead */}
        <div
          className="absolute inset-y-0 w-0.5 bg-white pointer-events-none z-20"
          style={{ left: `${playheadPct}%` }}
        />
      </div>
    </div>
  )
}
