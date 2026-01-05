import React from 'react'

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
  const SEGMENT_DURATION = 30 // Fixed 30 seconds

  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStart = parseFloat(e.target.value)
    // Ensure end time doesn't exceed duration
    const maxStart = Math.max(0, duration - SEGMENT_DURATION)
    const clampedStart = Math.min(newStart, maxStart)
    onTimeSelect(clampedStart, clampedStart + SEGMENT_DURATION)
    onSeek(clampedStart)
  }

  const maxStartTime = Math.max(0, duration - SEGMENT_DURATION)

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="w-full h-full relative group bg-[#0b0f14] select-none">
      {/* Background Track (Visual representation of full song) */}
      <div className="absolute inset-0 flex items-center opacity-20 px-2">
        <div className="w-full h-1/3 bg-slate-700/50 rounded-full" />
      </div>

      {/* Progress Bar (Current Playback) */}
      <div
        className="absolute top-0 bottom-0 left-0 bg-white/5 transition-all duration-100 pointer-events-none"
        style={{ width: `${(currentTime / (duration || 1)) * 100}%` }}
      />
      
      {/* Playhead Line */}
      <div
        className="absolute top-0 bottom-0 w-px bg-white/30 z-10 pointer-events-none"
        style={{ left: `${(currentTime / (duration || 1)) * 100}%` }}
      />

      {/* Selected Region Highlight */}
      <div
        className="absolute top-0 bottom-0 bg-neon-green/10 border-x border-neon-green/50 backdrop-blur-[1px] transition-all duration-75 cursor-grab active:cursor-grabbing"
        style={{
          left: `${(startTime / (duration || 1)) * 100}%`,
          width: `${(SEGMENT_DURATION / (duration || 1)) * 100}%`,
        }}
      >
        <div className="absolute top-0 left-0 bg-neon-green text-black text-[9px] font-bold px-1 rounded-br">
          {formatTime(startTime)}
        </div>
        <div className="absolute bottom-0 right-0 bg-neon-green text-black text-[9px] font-bold px-1 rounded-tl">
          {formatTime(endTime)}
        </div>
        
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <span className="text-[10px] font-mono text-neon-green font-bold tracking-widest bg-black/50 px-2 py-1 rounded">DRAG REGION</span>
        </div>
      </div>

      {/* Invisible Range Input for Interaction */}
      <input
        type="range"
        min="0"
        max={maxStartTime}
        step="0.1"
        value={startTime}
        onChange={handleStartTimeChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
      />
    </div>
  )
}
