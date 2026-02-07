import { Music, Activity, Layers } from 'lucide-react';
import { useState } from 'react';
import Card from '../../ui/Card';
import MusicTimeline from '../MusicTimeline';
import BeatTimeline from '../BeatTimeline';
import UnifiedTimeline from './UnifiedTimeline';
import { cn } from '../../ui/utils';

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

interface TimelinePanelProps {
    music: File | null;
    currentTime: number;
    duration: number;
    isPlaying: boolean;
    musicStartTime: number;
    musicEndTime: number;
    onTimeSelect: (start: number, end: number) => void;
    onTogglePlay: () => void;
    onSeek: (time: number) => void;
    beats: number[];
    proposedCuts: any[];
    onAcceptedCuts: (cuts: number[]) => void;
    playPending: boolean;
    zoom: number;
    onZoomChange: (val: number) => void;
    onAnalyze: () => void;
    analyzing: boolean;
    // New props for unified timeline
    clips?: ClipMeta[];
    selectedClipId?: string | null;
    onClipSelect?: (id: string | null) => void;
}

export default function TimelinePanel({
    music,
    currentTime,
    duration,
    isPlaying,
    musicStartTime,
    musicEndTime,
    onTimeSelect,
    onTogglePlay,
    onSeek,
    beats,
    proposedCuts,
    onAcceptedCuts,
    playPending,
    zoom,
    onZoomChange,
    onAnalyze,
    analyzing,
    clips = [],
    selectedClipId,
    onClipSelect
}: TimelinePanelProps) {
    const [viewMode, setViewMode] = useState<'unified' | 'beats'>('unified');
    
    return (
        <Card variant="glass" padding="none" className="h-full flex flex-col border-white/5 overflow-hidden">
            {/* Header */}
            <div className="px-3 py-1.5 border-b border-white/5 flex items-center justify-between bg-canvas/80 shrink-0">
                <div className="flex items-center gap-3">
                    {music && (
                        <button
                            onClick={onTogglePlay}
                            disabled={playPending}
                            className="w-7 h-7 flex items-center justify-center rounded-lg bg-reel text-canvas hover:bg-reel/90 transition-all"
                        >
                            {isPlaying ? <Activity className="w-3.5 h-3.5" /> : <Music className="w-3.5 h-3.5" />}
                        </button>
                    )}
                    
                    {/* View Mode Toggle */}
                    <div className="flex items-center gap-0.5 p-0.5 bg-black/30 rounded-md">
                        <button
                            onClick={() => setViewMode('unified')}
                            className={cn(
                                "px-2 py-1 rounded text-[9px] font-semibold flex items-center gap-1 transition-all",
                                viewMode === 'unified' 
                                    ? "bg-reel/20 text-reel" 
                                    : "text-text-muted hover:text-text-primary"
                            )}
                        >
                            <Layers size={10} />
                            Tracks
                        </button>
                        <button
                            onClick={() => setViewMode('beats')}
                            className={cn(
                                "px-2 py-1 rounded text-[9px] font-semibold flex items-center gap-1 transition-all",
                                viewMode === 'beats' 
                                    ? "bg-reel/20 text-reel" 
                                    : "text-text-muted hover:text-text-primary"
                            )}
                        >
                            <Activity size={10} />
                            Beats
                        </button>
                    </div>
                    
                    <span className="text-[10px] font-mono text-text-muted">
                        {music ? `${(musicEndTime - musicStartTime).toFixed(1)}s` : 'Timeline'}
                    </span>
                </div>

                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 px-2 py-1 rounded bg-white/5">
                        <span className="text-[9px] text-text-muted">Zoom</span>
                        <input
                            type="range"
                            min="0.5"
                            max="10"
                            step="0.5"
                            value={zoom}
                            onChange={(e) => onZoomChange(parseFloat(e.target.value))}
                            className="w-12 h-1 bg-white/10 rounded-full appearance-none cursor-pointer accent-reel"
                        />
                    </div>

                    {music && viewMode === 'beats' && (
                        <button
                            onClick={onAnalyze}
                            disabled={analyzing}
                            className="px-2 py-1 text-[9px] rounded bg-white/5 text-text-muted hover:bg-white/10 transition-all flex items-center gap-1"
                        >
                            {analyzing ? <div className="w-2 h-2 border border-reel border-t-transparent rounded-full animate-spin" /> : <Activity className="w-3 h-3 text-reel" />}
                            Sync
                        </button>
                    )}
                </div>
            </div>

            <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                {viewMode === 'unified' ? (
                    /* Unified Timeline View */
                    <>
                        {/* Mini waveform for region selection */}
                        {music && (
                            <div className="h-8 shrink-0 border-b border-white/5">
                                <MusicTimeline
                                    musicFile={music}
                                    onTimeSelect={onTimeSelect}
                                    currentTime={currentTime}
                                    duration={duration}
                                    isPlaying={isPlaying}
                                    onTogglePlay={onTogglePlay}
                                    onSeek={onSeek}
                                    startTime={musicStartTime}
                                    endTime={musicEndTime}
                                />
                            </div>
                        )}
                        
                        {/* Unified Media Timeline */}
                        <div className="flex-1 min-h-0 overflow-hidden">
                            <UnifiedTimeline
                                clips={clips}
                                audioFile={music}
                                audioStartTime={musicStartTime}
                                audioEndTime={musicEndTime}
                                currentTime={currentTime}
                                isPlaying={isPlaying}
                                onTogglePlay={onTogglePlay}
                                onSeek={onSeek}
                                selectedClipId={selectedClipId}
                                onClipSelect={onClipSelect}
                                zoom={zoom}
                                onZoomChange={onZoomChange}
                            />
                        </div>
                    </>
                ) : (
                    /* Beat Analysis View */
                    music ? (
                        <>
                            {/* Mini waveform for region selection */}
                            <div className="h-10 shrink-0 border-b border-white/5">
                                <MusicTimeline
                                    musicFile={music}
                                    onTimeSelect={onTimeSelect}
                                    currentTime={currentTime}
                                    duration={duration}
                                    isPlaying={isPlaying}
                                    onTogglePlay={onTogglePlay}
                                    onSeek={onSeek}
                                    startTime={musicStartTime}
                                    endTime={musicEndTime}
                                />
                            </div>

                            {/* Beat Waveform */}
                            <div className="flex-1 min-h-0">
                                <BeatTimeline
                                    musicFile={music}
                                    beats={beats}
                                    proposedCuts={proposedCuts}
                                    currentTime={currentTime}
                                    isPlaying={isPlaying}
                                    onTogglePlay={onTogglePlay}
                                    onSeek={onSeek}
                                    regionStart={musicStartTime}
                                    regionEnd={musicEndTime}
                                    onSelectCut={onSeek}
                                    onAcceptedCuts={onAcceptedCuts}
                                    playPending={playPending}
                                    zoom={zoom}
                                />
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                                <Music className="w-6 h-6 text-text-muted/40 mx-auto mb-2" />
                                <p className="text-[10px] text-text-muted">Add audio for beat analysis</p>
                            </div>
                        </div>
                    )
                )}
            </div>
        </Card>
    );
}
