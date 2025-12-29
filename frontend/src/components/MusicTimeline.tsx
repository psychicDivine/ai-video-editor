import { useState, useRef, useEffect } from 'react'

interface MusicTimelineProps {
  musicFile: File
  onTimeSelect: (startTime: number, endTime: number) => void
}

export default function MusicTimeline({ musicFile, onTimeSelect }: MusicTimelineProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [duration, setDuration] = useState(0)
  const [startTime, setStartTime] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const SEGMENT_DURATION = 30 // Fixed 30 seconds

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleLoadedMetadata = () => {
      setDuration(audio.duration)
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
    }

    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('timeupdate', handleTimeUpdate)

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('timeupdate', handleTimeUpdate)
    }
  }, [])

  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStart = parseFloat(e.target.value)
    // Ensure end time doesn't exceed duration
    const maxStart = Math.max(0, duration - SEGMENT_DURATION)
    const clampedStart = Math.min(newStart, maxStart)
    setStartTime(clampedStart)
    onTimeSelect(clampedStart, clampedStart + SEGMENT_DURATION)
  }

  const endTime = Math.min(startTime + SEGMENT_DURATION, duration)
  const maxStartTime = Math.max(0, duration - SEGMENT_DURATION)

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-4">
      {/* Audio Player */}
      <div>
        <audio
          ref={audioRef}
          src={URL.createObjectURL(musicFile)}
          controls
          className="w-full h-8 bg-slate-800 rounded"
        />
      </div>

      {/* Timeline Info */}
      <div className="bg-slate-600 bg-opacity-50 p-4 rounded border border-slate-500">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-slate-400">Start Time</p>
            <p className="text-lg font-bold text-blue-400">{formatTime(startTime)}</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Duration</p>
            <p className="text-lg font-bold text-green-400">{SEGMENT_DURATION}s</p>
          </div>
          <div>
            <p className="text-xs text-slate-400">End Time</p>
            <p className="text-lg font-bold text-purple-400">{formatTime(endTime)}</p>
          </div>
        </div>
      </div>

      {/* Timeline Slider */}
      <div>
        <label className="block text-sm font-medium text-slate-200 mb-3">
          📍 Select where to start your 30-second clip
        </label>

        {/* Visual Timeline */}
        <div className="relative mb-4">
          {/* Background bar */}
          <div className="h-2 bg-slate-600 rounded-full overflow-hidden">
            {/* Played portion */}
            <div
              className="h-full bg-blue-500 transition-all"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>

          {/* Selected segment indicator */}
          <div
            className="absolute top-0 h-2 bg-green-500 opacity-50 rounded-full pointer-events-none"
            style={{
              left: `${(startTime / duration) * 100}%`,
              width: `${(SEGMENT_DURATION / duration) * 100}%`,
            }}
          />
        </div>

        {/* Slider Input */}
        <input
          type="range"
          min="0"
          max={maxStartTime}
          step="0.1"
          value={startTime}
          onChange={handleStartTimeChange}
          className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer"
        />

        {/* Time Labels */}
        <div className="flex justify-between text-xs text-slate-400 mt-2">
          <span>0:00</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-slate-700 bg-opacity-50 p-3 rounded border border-slate-600">
        <p className="text-xs text-slate-300">
          💡 <span className="font-semibold">Tip:</span> Drag the slider to select the best 30-second segment from your music. The green highlight shows your selected segment.
        </p>
      </div>
    </div>
  )
}
