import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import { Film, Music, ZoomIn, ZoomOut, Play, Pause } from 'lucide-react';
import { cn } from '../../ui/utils';
import { formatDuration } from '../../utils/videoMetadata';

interface ClipMeta {
    id: string;
    file: File;
    url: string;
    createdAt: number;
    isPrimary: boolean;
    duration?: number;
    width?: number;
    height?: number;
    thumbnails?: string[];
    inPoint?: number;
    outPoint?: number;
}

interface UnifiedTimelineProps {
    clips: ClipMeta[];
    audioFile: File | null;
    audioStartTime: number;
    audioEndTime: number;
    currentTime: number;
    isPlaying: boolean;
    onTogglePlay: () => void;
    onSeek: (time: number) => void;
    onClipSelect?: (id: string | null) => void;
    selectedClipId?: string | null;
    zoom: number;
    onZoomChange: (zoom: number) => void;
}

export default function UnifiedTimeline({
    clips,
    audioFile,
    audioStartTime,
    audioEndTime,
    currentTime,
    isPlaying,
    onTogglePlay,
    onSeek,
    onClipSelect,
    selectedClipId,
    zoom,
    onZoomChange
}: UnifiedTimelineProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const videoTrackRef = useRef<HTMLDivElement>(null);
    const [containerWidth, setContainerWidth] = useState(800);
    
    // Calculate timeline duration (max of audio region or total clip duration)
    const clipsTotalDuration = useMemo(() => 
        clips.reduce((acc, clip) => {
            const clipDur = (clip.outPoint ?? clip.duration ?? 0) - (clip.inPoint ?? 0);
            return acc + clipDur;
        }, 0),
        [clips]
    );
    
    const audioDur = audioEndTime - audioStartTime;
    const timelineDuration = Math.max(clipsTotalDuration, audioDur, 30);
    
    // Pixels per second based on zoom
    const pixelsPerSecond = useMemo(() => {
        const baseWidth = containerWidth - 40; // padding
        const basePPS = baseWidth / timelineDuration;
        return basePPS * zoom;
    }, [containerWidth, timelineDuration, zoom]);
    
    // Resize observer
    useEffect(() => {
        if (!containerRef.current) return;
        const observer = new ResizeObserver(entries => {
            setContainerWidth(entries[0].contentRect.width);
        });
        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);
    
    // Time ruler marks
    const rulerMarks = useMemo(() => {
        const marks: { time: number; label: string; major: boolean }[] = [];
        const interval = zoom > 3 ? 1 : zoom > 1.5 ? 5 : 10;
        
        for (let t = 0; t <= timelineDuration; t += interval) {
            marks.push({
                time: t,
                label: formatDuration(t),
                major: t % (interval * 2) === 0
            });
        }
        return marks;
    }, [timelineDuration, zoom]);
    
    // Click to seek
    const handleTimelineClick = useCallback((e: React.MouseEvent) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const time = x / pixelsPerSecond;
        onSeek(Math.max(0, Math.min(time, timelineDuration)));
    }, [pixelsPerSecond, timelineDuration, onSeek]);
    
    // Playhead position
    const playheadX = (currentTime - audioStartTime) * pixelsPerSecond;
    
    // Calculate clip positions on timeline
    const clipPositions = useMemo(() => {
        let currentX = 0;
        return clips.map(clip => {
            const inPoint = clip.inPoint ?? 0;
            const outPoint = clip.outPoint ?? clip.duration ?? 5;
            const duration = outPoint - inPoint;
            const width = duration * pixelsPerSecond;
            const x = currentX;
            currentX += width + 2; // 2px gap between clips
            return { clip, x, width, duration };
        });
    }, [clips, pixelsPerSecond]);
    
    return (
        <div className="h-full flex flex-col bg-canvas/50 rounded-lg border border-white/5 overflow-hidden">
            {/* Timeline Header */}
            <div className="h-8 px-3 flex items-center justify-between border-b border-white/5 bg-black/30 shrink-0">
                <div className="flex items-center gap-3">
                    <button
                        onClick={onTogglePlay}
                        className={cn(
                            "w-7 h-7 rounded-lg flex items-center justify-center transition-all",
                            isPlaying 
                                ? "bg-reel text-canvas" 
                                : "bg-white/10 text-text-primary hover:bg-reel hover:text-canvas"
                        )}
                    >
                        {isPlaying ? <Pause size={14} /> : <Play size={14} className="ml-0.5" />}
                    </button>
                    <div className="text-[10px] font-mono text-text-muted">
                        <span className="text-reel">{formatDuration(currentTime)}</span>
                        <span className="mx-1">/</span>
                        <span>{formatDuration(timelineDuration)}</span>
                    </div>
                </div>
                
                {/* Zoom Controls */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => onZoomChange(Math.max(0.5, zoom - 0.5))}
                        className="w-6 h-6 rounded flex items-center justify-center bg-white/5 text-text-muted hover:bg-white/10 hover:text-text-primary transition-colors"
                    >
                        <ZoomOut size={12} />
                    </button>
                    <span className="text-[9px] font-mono text-text-muted w-8 text-center">
                        {Math.round(zoom * 100)}%
                    </span>
                    <button
                        onClick={() => onZoomChange(Math.min(10, zoom + 0.5))}
                        className="w-6 h-6 rounded flex items-center justify-center bg-white/5 text-text-muted hover:bg-white/10 hover:text-text-primary transition-colors"
                    >
                        <ZoomIn size={12} />
                    </button>
                </div>
            </div>
            
            {/* Timeline Body */}
            <div 
                ref={containerRef}
                className="flex-1 overflow-hidden"
            >
                <div 
                    className="relative h-full"
                    style={{ width: '100%' }}
                    onClick={handleTimelineClick}
                >
                    {/* Time Ruler */}
                    <div className="h-5 border-b border-white/10 relative">
                        {rulerMarks.map((mark, i) => (
                            <div 
                                key={i}
                                className="absolute top-0 flex flex-col items-center"
                                style={{ left: mark.time * pixelsPerSecond }}
                            >
                                <div className={cn(
                                    "w-px",
                                    mark.major ? "h-3 bg-text-muted/50" : "h-2 bg-text-muted/30"
                                )} />
                                {mark.major && (
                                    <span className="text-[8px] font-mono text-text-muted/60 mt-0.5">
                                        {mark.label}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                    
                    {/* Video Track */}
                    <div className="h-16 relative border-b border-white/5">
                        {/* Track Label */}
                        <div className="absolute left-0 top-0 bottom-0 w-8 bg-black/40 border-r border-white/5 flex items-center justify-center z-10">
                            <Film size={12} className="text-reel/60" />
                        </div>
                        
                        {/* Clips */}
                        <div ref={videoTrackRef} className="absolute left-8 right-0 top-1 bottom-1">
                            {clipPositions.map(({ clip, x, width, duration }) => (
                                <div
                                    key={clip.id}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onClipSelect?.(selectedClipId === clip.id ? null : clip.id);
                                    }}
                                    className={cn(
                                        "absolute top-0 bottom-0 rounded-md overflow-hidden cursor-pointer transition-all",
                                        selectedClipId === clip.id
                                            ? "ring-2 ring-reel shadow-[0_0_12px_rgba(0,240,255,0.4)]"
                                            : clip.isPrimary
                                                ? "ring-1 ring-reel/40"
                                                : "ring-1 ring-white/10 hover:ring-white/30"
                                    )}
                                    style={{ left: x, width: Math.max(width, 20) }}
                                >
                                    {/* Filmstrip Background */}
                                    <div className="absolute inset-0 flex">
                                        {clip.thumbnails && clip.thumbnails.length > 0 ? (
                                            clip.thumbnails.map((thumb, i) => (
                                                <img
                                                    key={i}
                                                    src={thumb}
                                                    alt=""
                                                    className="h-full object-cover flex-1"
                                                    style={{ minWidth: 0 }}
                                                />
                                            ))
                                        ) : (
                                            <div className="w-full h-full bg-gradient-to-r from-reel/20 to-reel/10 flex items-center justify-center">
                                                <Film size={16} className="text-reel/40" />
                                            </div>
                                        )}
                                    </div>
                                    
                                    {/* Overlay */}
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                                    
                                    {/* Clip Info */}
                                    <div className="absolute bottom-0.5 left-1 right-1 flex items-center justify-between">
                                        <span className="text-[8px] font-medium text-white truncate max-w-[60%]">
                                            {clip.file.name.split('.')[0]}
                                        </span>
                                        <span className="text-[7px] font-mono text-white/70">
                                            {formatDuration(duration)}
                                        </span>
                                    </div>
                                    
                                    {/* Primary Badge */}
                                    {clip.isPrimary && (
                                        <div className="absolute top-0.5 left-0.5 bg-reel px-1 py-0.5 rounded text-[6px] font-bold text-canvas">
                                            ★
                                        </div>
                                    )}
                                    
                                    {/* Trim Handles */}
                                    {selectedClipId === clip.id && (
                                        <>
                                            <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-reel cursor-ew-resize hover:bg-white transition-colors" />
                                            <div className="absolute right-0 top-0 bottom-0 w-1.5 bg-reel cursor-ew-resize hover:bg-white transition-colors" />
                                        </>
                                    )}
                                </div>
                            ))}
                            
                            {/* Empty State */}
                            {clips.length === 0 && (
                                <div className="absolute inset-0 flex items-center justify-center text-[10px] text-text-muted">
                                    Add video clips to see them here
                                </div>
                            )}
                        </div>
                    </div>
                    
                    {/* Audio Track */}
                    <div className="h-12 relative">
                        {/* Track Label */}
                        <div className="absolute left-0 top-0 bottom-0 w-8 bg-black/40 border-r border-white/5 flex items-center justify-center z-10">
                            <Music size={12} className="text-primary/60" />
                        </div>
                        
                        {/* Audio Waveform Placeholder */}
                        <div className="absolute left-8 right-0 top-1 bottom-1">
                            {audioFile ? (
                                <div 
                                    className="h-full rounded-md bg-gradient-to-r from-primary/20 via-primary/30 to-primary/20 border border-primary/30 relative overflow-hidden"
                                    style={{ 
                                        width: audioDur * pixelsPerSecond,
                                        marginLeft: 0 // Audio starts at 0 in this view
                                    }}
                                >
                                    {/* Waveform pattern */}
                                    <div className="absolute inset-0 flex items-center justify-center gap-[1px] px-2">
                                        {Array.from({ length: Math.min(100, Math.floor(audioDur * 3)) }).map((_, i) => (
                                            <div
                                                key={i}
                                                className="w-[2px] bg-primary/60 rounded-full"
                                                style={{ 
                                                    height: `${20 + Math.sin(i * 0.5) * 30 + Math.random() * 20}%`
                                                }}
                                            />
                                        ))}
                                    </div>
                                    
                                    {/* Audio Info */}
                                    <div className="absolute bottom-0.5 left-1 text-[8px] font-medium text-white/80 truncate">
                                        {audioFile.name}
                                    </div>
                                    <div className="absolute bottom-0.5 right-1 text-[7px] font-mono text-white/60">
                                        {formatDuration(audioDur)}
                                    </div>
                                </div>
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center text-[10px] text-text-muted">
                                    Add audio track
                                </div>
                            )}
                        </div>
                    </div>
                    
                    {/* Playhead */}
                    {currentTime >= audioStartTime && currentTime <= audioEndTime && (
                        <div 
                            className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_8px_rgba(255,255,255,0.5)] z-20 pointer-events-none"
                            style={{ left: playheadX + 32 }} // +32 for track label width
                        >
                            <div className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rounded-full shadow-lg" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
