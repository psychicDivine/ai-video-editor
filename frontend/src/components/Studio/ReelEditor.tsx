import React, { useEffect, useRef, useState, useCallback, type ChangeEvent, type DragEvent } from 'react';
import axios from 'axios';
import AssetsPanel from './AssetsPanel';
import PreviewPanel from './PreviewPanel';
import TimelinePanel from './TimelinePanel';
import ProjectWizard from './ProjectWizard';
import DropOverlay from './DropOverlay';
import Button from '../../ui/Button';
import { Sparkles, Loader2 } from 'lucide-react';
import Card from '../../ui/Card';
import StyleSelector from '../StyleSelector';
import { extractVideoMetadata } from '../../utils/videoMetadata';

type ClipMeta = {
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
};

interface ReelEditorProps {
    onJobCreated: (jobId: string) => void;
    style: string;
}

const CLIP_LIMIT = 15;

export default function ReelEditor({ onJobCreated, style }: ReelEditorProps) {
    // --- State from UploadForm ---
    const [clips, setClips] = useState<ClipMeta[]>([]);
    const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
    const [music, setMusic] = useState<File | null>(null);
    const [musicUrl, setMusicUrl] = useState<string | null>(null);
    const [musicStartTime, setMusicStartTime] = useState(0);
    const [musicEndTime, setMusicEndTime] = useState(30);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [beats, setBeats] = useState<number[]>([]);
    const [proposedCuts, setProposedCuts] = useState<any[]>([]);
    const [acceptedCuts, setAcceptedCuts] = useState<number[]>([]);
    const [analyzing, setAnalyzing] = useState(false);
    const [hoveredClip, setHoveredClip] = useState<ClipMeta | null>(null);
    const [showWizard, setShowWizard] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [dragType, setDragType] = useState<'video' | 'audio' | 'mixed' | null>(null);
    const dragCounter = useRef(0);

    const audioRef = useRef<HTMLAudioElement>(null);
    const previewVideoRef = useRef<HTMLVideoElement>(null);
    const videoInputRef = useRef<HTMLInputElement>(null);
    const musicInputRef = useRef<HTMLInputElement>(null);

    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playPending, setPlayPending] = useState(false);
    const [zoom, setZoom] = useState(1);

    const handleAnalyze = async () => {
        if (!music) return;
        setAnalyzing(true);
        try {
            const fd = new FormData();
            fd.append('audio', music);
            const query = `?start=${musicStartTime}&end=${musicEndTime}`;
            const resp = await fetch('/api/analyze-beats' + query, { method: 'POST', body: fd });
            if (!resp.ok) throw new Error('Analysis failed');
            const data = await resp.json();
            setBeats(data.beats || []);
            setProposedCuts(data.proposedCuts || []);
        } catch (err) {
            console.error(err);
            setError('Beat analysis failed. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    // --- Logic from UploadForm ---
    useEffect(() => {
        if (!music) {
            setMusicUrl(null);
            return;
        }
        const url = URL.createObjectURL(music);
        setMusicUrl(url);
        return () => URL.revokeObjectURL(url);
    }, [music]);

    useEffect(() => {
        if (!music || !audioRef.current) return;
        setIsPlaying(false);
        setCurrentTime(0);
        setDuration(0);
        setBeats([]);
        setProposedCuts([]);
    }, [music]);

    useEffect(() => {
        if (!music) return;
        const timer = setTimeout(() => {
            handleAnalyze();
        }, 800);
        return () => clearTimeout(timer);
    }, [music, musicStartTime, musicEndTime]);

    const handleTimeUpdate = () => {
        if (!audioRef.current) return;
        const t = audioRef.current.currentTime;
        setCurrentTime(t);
        if (isPlaying && (t < musicStartTime || t >= musicEndTime)) {
            audioRef.current.currentTime = musicStartTime;
        }
    };

    const togglePlay = async () => {
        if (!audioRef.current || playPending) return;
        setPlayPending(true);
        try {
            if (isPlaying) {
                audioRef.current.pause();
                setIsPlaying(false);
            } else {
                if (currentTime < musicStartTime || currentTime >= musicEndTime) {
                    audioRef.current.currentTime = musicStartTime;
                }
                await audioRef.current.play();
                setIsPlaying(true);
            }
        } catch (err) {
            setIsPlaying(false);
        } finally {
            setPlayPending(false);
        }
    };

    const seek = (time: number) => {
        if (!audioRef.current) return;
        audioRef.current.currentTime = time;
        setCurrentTime(time);
    };

    const handleVideoChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files) return;
        const available = CLIP_LIMIT - clips.length;
        if (available <= 0) return;
        const baseTimestamp = Date.now();
        const additions = Array.from(e.target.files)
            .slice(0, available)
            .map((file, index) => ({
                id: `${baseTimestamp}-${index}`,
                file,
                url: URL.createObjectURL(file),
                createdAt: baseTimestamp + index,
                isPrimary: clips.length === 0 && index === 0,
            }));
        setClips([...clips, ...additions]);
        
        // Extract metadata for each clip
        additions.forEach(clip => {
            extractVideoMetadata(clip.file).then(meta => {
                setClips(prev => prev.map(c => 
                    c.id === clip.id ? { ...c, ...meta } : c
                ));
            }).catch(console.error);
        });
    };

    // Drag-drop handlers
    const detectFileType = useCallback((e: DragEvent): 'video' | 'audio' | 'mixed' | null => {
        const items = e.dataTransfer?.items;
        if (!items || items.length === 0) return null;
        
        let hasVideo = false;
        let hasAudio = false;
        
        for (let i = 0; i < items.length; i++) {
            const type = items[i].type;
            if (type.startsWith('video/')) hasVideo = true;
            else if (type.startsWith('audio/')) hasAudio = true;
        }
        
        if (hasVideo && hasAudio) return 'mixed';
        if (hasVideo) return 'video';
        if (hasAudio) return 'audio';
        return null;
    }, []);

    const handleDragEnter = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current++;
        
        if (dragCounter.current === 1) {
            setIsDragging(true);
            setDragType(detectFileType(e));
        }
    }, [detectFileType]);

    const handleDragOver = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDragLeave = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current--;
        
        if (dragCounter.current === 0) {
            setIsDragging(false);
            setDragType(null);
        }
    }, []);

    const handleDrop = useCallback((e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current = 0;
        setIsDragging(false);
        setDragType(null);
        
        const files = Array.from(e.dataTransfer?.files || []);
        if (files.length === 0) return;
        
        // Separate videos and audio
        const videoFiles = files.filter(f => f.type.startsWith('video/'));
        const audioFiles = files.filter(f => f.type.startsWith('audio/'));
        
        // Add video clips
        if (videoFiles.length > 0) {
            const available = CLIP_LIMIT - clips.length;
            if (available > 0) {
                const baseTimestamp = Date.now();
                const additions = videoFiles.slice(0, available).map((file, index) => ({
                    id: `${baseTimestamp}-${index}`,
                    file,
                    url: URL.createObjectURL(file),
                    createdAt: baseTimestamp + index,
                    isPrimary: clips.length === 0 && index === 0,
                }));
                setClips(prev => [...prev, ...additions]);
                
                // Extract metadata for each clip
                additions.forEach(clip => {
                    extractVideoMetadata(clip.file).then(meta => {
                        setClips(prev => prev.map(c => 
                            c.id === clip.id ? { ...c, ...meta } : c
                        ));
                    }).catch(console.error);
                });
            }
        }
        
        // Set audio (first audio file wins)
        if (audioFiles.length > 0 && !music) {
            setMusic(audioFiles[0]);
        }
    }, [clips.length, music]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (clips.length === 0 || !music) {
            setError('Missing assets');
            return;
        }
        setLoading(true);
        try {
            const formData = new FormData();
            clips.forEach(c => formData.append('videos', c.file));
            formData.append('music', music);
            formData.append('style', style);
            formData.append('music_start_time', musicStartTime.toString());
            formData.append('music_end_time', musicEndTime.toString());
            if (acceptedCuts.length) formData.append('accepted_cuts', JSON.stringify(acceptedCuts));

            const response = await axios.post('/api/upload', formData);
            onJobCreated(response.data.job_id);
        } catch (err: any) {
            setError(err.message || 'Upload failed');
        } finally {
            setLoading(false);
        }
    };

    const handleLoadedMetadata = () => {
        if (!audioRef.current) return;
        setDuration(audioRef.current.duration);
        audioRef.current.volume = 1.0;
        audioRef.current.muted = false;
    };

    const handleProjectStart = (videos: File[], audio: File) => {
        // Create ClipMeta objects from video files
        const baseTimestamp = Date.now();
        const newClips: ClipMeta[] = videos.map((file, index) => ({
            id: `${baseTimestamp}-${index}`,
            file,
            url: URL.createObjectURL(file),
            createdAt: baseTimestamp + index,
            isPrimary: index === 0, // First clip is primary
        }));

        // Set audio
        setMusic(audio);
        setClips(newClips);
        setShowWizard(false); // Close the wizard
        
        // Extract metadata for each clip
        newClips.forEach(clip => {
            extractVideoMetadata(clip.file).then(meta => {
                setClips(prev => prev.map(c => 
                    c.id === clip.id ? { ...c, ...meta } : c
                ));
            }).catch(console.error);
        });
    };

    return (
        <>
            {showWizard && (
                <ProjectWizard 
                    onComplete={handleProjectStart}
                    onSkip={() => setShowWizard(false)}
                />
            )}
            <div 
                className="h-full flex flex-col p-3 overflow-hidden relative"
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
            <DropOverlay visible={isDragging} dragType={dragType} />
            {musicUrl && (
                <audio
                    ref={audioRef}
                    src={musicUrl}
                    onTimeUpdate={handleTimeUpdate}
                    onLoadedMetadata={handleLoadedMetadata}
                    onEnded={() => setIsPlaying(false)}
                    onError={(e) => console.error('Audio issue:', e)}
                    className="hidden"
                />
            )}

            {/* Expert Workspace Layout - 2:8:2 Pro Distribution */}
            <div className="flex-1 grid grid-cols-12 gap-3 min-h-0 overflow-hidden">

                {/* Left Panel: Asset Library - COMPACT (2cols) */}
                <div className="col-span-2 flex flex-col min-h-0">
                    <AssetsPanel
                            clips={clips}
                            onClipsChange={setClips}
                            onUpload={() => videoInputRef.current?.click()}
                            onRemove={(id) => setClips(clips.filter(c => c.id !== id))}
                            onSetPrimary={(id) => setClips(clips.map(c => ({ ...c, isPrimary: c.id === id })))}
                            onHover={setHoveredClip}
                            audioFile={music}
                            onAudioUpload={() => musicInputRef.current?.click()}
                            onAudioRemove={() => setMusic(null)}
                            selectedClipId={selectedClipId}
                            onClipSelect={setSelectedClipId}
                        />
                </div>

                {/* Center Panel: Production Deck - EXPANDED (8cols) */}
                <div className="col-span-8 flex flex-col gap-2 min-h-0 overflow-hidden">
                    {/* Preview - takes remaining space after timeline */}
                    <div className="flex-[3] min-h-0 group/preview relative overflow-hidden">
                        <PreviewPanel videoRef={previewVideoRef} hoveredClipUrl={hoveredClip?.url || null} />
                    </div>
                    {/* Timeline - fixed proportion */}
                    <div className="flex-[2] min-h-0 overflow-hidden">
                        <TimelinePanel
                            music={music}
                            currentTime={currentTime}
                            duration={duration}
                            isPlaying={isPlaying}
                            musicStartTime={musicStartTime}
                            musicEndTime={musicEndTime}
                            onTimeSelect={(s, e) => { setMusicStartTime(s); setMusicEndTime(e); }}
                            onTogglePlay={togglePlay}
                            onSeek={seek}
                            beats={beats}
                            proposedCuts={proposedCuts}
                            onAcceptedCuts={setAcceptedCuts}
                            playPending={playPending}
                            zoom={zoom}
                            onZoomChange={setZoom}
                            onAnalyze={handleAnalyze}
                            analyzing={analyzing}
                            clips={clips}
                            selectedClipId={selectedClipId}
                            onClipSelect={setSelectedClipId}
                        />
                    </div>
                </div>

                {/* Right Panel: Style & Action (2cols) */}
                <div className="col-span-2 flex flex-col min-h-0 hidden xl:flex">
                    <Card variant="glass" padding="none" className="flex-1 flex flex-col overflow-hidden">
                        {/* Style Selection - Compact */}
                        <div className="flex-1 overflow-hidden p-3">
                            <StyleSelector selectedStyle={style} onStyleChange={() => { }} />
                        </div>

                        {/* Action Footer - Always Visible */}
                        <div className="p-3 border-t border-white/5 bg-canvas/50">
                            {error && (
                                <div className="mb-2 p-2 bg-danger/10 border border-danger/20 rounded-lg">
                                    <p className="text-[9px] text-danger leading-tight">{error}</p>
                                </div>
                            )}

                            <Button
                                variant="reel"
                                size="lg"
                                className="w-full h-12 rounded-lg"
                                disabled={loading || clips.length === 0 || !music}
                                onClick={handleSubmit}
                            >
                                <span className="flex items-center justify-center gap-2">
                                    {loading ? (
                                        <Loader2 size={16} className="animate-spin" />
                                    ) : (
                                        <>
                                            <Sparkles size={14} />
                                            <span className="text-sm font-bold">Create Reel</span>
                                        </>
                                    )}
                                </span>
                            </Button>
                        </div>
                    </Card>
                </div>
            </div>

            {/* Hidden Inputs */}
            <input ref={videoInputRef} type="file" multiple accept="video/*" className="hidden" onChange={handleVideoChange} />
            <input ref={musicInputRef} type="file" accept="audio/*" className="hidden" onChange={(e) => e.target.files && setMusic(e.target.files[0])} />
            </div>
        </>
    );
}
