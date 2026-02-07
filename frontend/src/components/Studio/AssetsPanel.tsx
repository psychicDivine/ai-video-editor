import { useState } from 'react';
import { Reorder } from 'framer-motion';
import { Plus, X, Star, Film, Music, Upload, GripVertical } from 'lucide-react';
import { cn } from '../../ui/utils';
import Card from '../../ui/Card';
import { formatDuration, formatResolution } from '../../utils/videoMetadata';

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
}

interface AssetsPanelProps {
    clips: ClipMeta[];
    onClipsChange: (clips: ClipMeta[]) => void;
    onUpload: () => void;
    onRemove: (id: string) => void;
    onSetPrimary: (id: string) => void;
    onHover: (clip: ClipMeta | null) => void;
    audioFile?: File | null;
    onAudioUpload?: () => void;
    onAudioRemove?: () => void;
    selectedClipId?: string | null;
    onClipSelect?: (id: string | null) => void;
}

export default function AssetsPanel({
    clips,
    onClipsChange,
    onUpload,
    onRemove,
    onSetPrimary,
    onHover,
    audioFile,
    onAudioUpload,
    onAudioRemove,
    selectedClipId,
    onClipSelect
}: AssetsPanelProps) {
    const [activeTab, setActiveTab] = useState<'video' | 'audio'>('video');
    
    // Calculate total duration
    const totalDuration = clips.reduce((acc, clip) => acc + (clip.duration || 0), 0);
    
    return (
        <Card variant="glass" padding="none" className="h-full flex flex-col">
            {/* Header with Stats */}
            <div className="px-3 py-2 border-b border-white/5">
                {/* Tab Pills */}
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1 p-0.5 bg-surface-elevated/50 rounded-lg">
                        <button
                            onClick={() => setActiveTab('video')}
                            className={cn(
                                'flex items-center gap-1.5 px-2.5 py-1.5 text-[10px] font-semibold rounded-md transition-all',
                                activeTab === 'video'
                                    ? 'bg-reel text-canvas'
                                    : 'text-text-secondary hover:text-text-primary'
                            )}
                        >
                            <Film size={11} />
                            <span>{clips.length}</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('audio')}
                            className={cn(
                                'flex items-center gap-1.5 px-2.5 py-1.5 text-[10px] font-semibold rounded-md transition-all',
                                activeTab === 'audio'
                                    ? 'bg-primary text-white'
                                    : 'text-text-secondary hover:text-text-primary'
                            )}
                        >
                            <Music size={11} />
                            <span>{audioFile ? '1' : '0'}</span>
                        </button>
                    </div>
                    
                    <button
                        onClick={activeTab === 'video' ? onUpload : onAudioUpload}
                        className="w-6 h-6 rounded-md bg-white/5 text-text-secondary hover:bg-reel hover:text-canvas transition-colors flex items-center justify-center"
                    >
                        <Plus size={12} />
                    </button>
                </div>
                
                {/* Stats Bar */}
                {activeTab === 'video' && clips.length > 0 && (
                    <div className="flex items-center justify-between text-[9px] font-mono text-text-muted">
                        <span>Total: {formatDuration(totalDuration)}</span>
                        <span>{clips.length}/15 clips</span>
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden p-2">
                {activeTab === 'video' ? (
                    clips.length > 0 ? (
                        <Reorder.Group
                            axis="y"
                            values={clips}
                            onReorder={onClipsChange}
                            className="flex flex-col gap-1"
                        >
                            {clips.map((clip) => (
                                <Reorder.Item
                                    key={clip.id}
                                    value={clip}
                                    onMouseEnter={() => onHover(clip)}
                                    onMouseLeave={() => onHover(null)}
                                    className="group"
                                >
                                    <div 
                                        onClick={() => onClipSelect?.(selectedClipId === clip.id ? null : clip.id)}
                                        className={cn(
                                            "flex items-center gap-2 p-1.5 rounded-lg border transition-all cursor-pointer",
                                            selectedClipId === clip.id
                                                ? "border-reel bg-reel/20 shadow-[0_0_10px_rgba(0,240,255,0.2)]"
                                                : clip.isPrimary 
                                                    ? "border-reel/30 bg-reel/5" 
                                                    : "border-transparent bg-white/5 hover:bg-white/10"
                                        )}
                                    >
                                        {/* Drag Handle */}
                                        <div className="cursor-grab active:cursor-grabbing text-text-muted/40 hover:text-text-muted">
                                            <GripVertical size={12} />
                                        </div>
                                        
                                        {/* Thumbnail */}
                                        <div className="relative w-14 h-10 rounded overflow-hidden shrink-0 bg-black">
                                            {clip.thumbnails && clip.thumbnails[0] ? (
                                                <img 
                                                    src={clip.thumbnails[0]} 
                                                    alt="" 
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <video
                                                    src={clip.url}
                                                    className="w-full h-full object-cover"
                                                />
                                            )}
                                            {clip.isPrimary && (
                                                <div className="absolute top-0.5 left-0.5">
                                                    <Star size={8} className="text-reel fill-reel" />
                                                </div>
                                            )}
                                            {/* Duration overlay */}
                                            {clip.duration && (
                                                <div className="absolute bottom-0 right-0 bg-black/80 px-1 py-0.5 text-[8px] font-mono text-white">
                                                    {formatDuration(clip.duration)}
                                                </div>
                                            )}
                                        </div>
                                        
                                        {/* Info */}
                                        <div className="flex-1 min-w-0">
                                            <p className="text-[10px] font-medium text-text-primary truncate">
                                                {clip.file.name}
                                            </p>
                                            <div className="flex items-center gap-2 text-[9px] text-text-muted">
                                                {clip.width && clip.height && (
                                                    <span>{formatResolution(clip.width, clip.height)}</span>
                                                )}
                                                <span>{(clip.file.size / (1024 * 1024)).toFixed(1)}MB</span>
                                            </div>
                                        </div>
                                        
                                        {/* Actions */}
                                        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); onSetPrimary(clip.id); }}
                                                className={cn(
                                                    "w-5 h-5 rounded flex items-center justify-center transition-colors",
                                                    clip.isPrimary 
                                                        ? "bg-reel text-canvas" 
                                                        : "bg-white/10 text-text-muted hover:text-reel"
                                                )}
                                                title="Set as primary"
                                            >
                                                <Star size={9} fill={clip.isPrimary ? "currentColor" : "none"} />
                                            </button>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); onRemove(clip.id); }}
                                                className="w-5 h-5 rounded bg-white/10 text-text-muted hover:bg-red-500/20 hover:text-red-400 flex items-center justify-center transition-colors"
                                                title="Remove clip"
                                            >
                                                <X size={9} />
                                            </button>
                                        </div>
                                    </div>
                                </Reorder.Item>
                            ))}
                            
                            {/* Add More */}
                            {clips.length < 15 && (
                                <button
                                    onClick={onUpload}
                                    className="flex items-center justify-center gap-2 p-2.5 rounded-lg border border-dashed border-white/10 text-text-muted hover:border-reel/50 hover:text-reel transition-colors"
                                >
                                    <Plus size={12} />
                                    <span className="text-[10px] font-medium">Add clips</span>
                                </button>
                            )}
                        </Reorder.Group>
                    ) : (
                        <button
                            onClick={onUpload}
                            className="w-full h-full min-h-[100px] flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-white/10 text-text-muted hover:border-reel/50 hover:text-reel transition-all"
                        >
                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                                <Upload size={16} />
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] font-semibold">Drop videos</p>
                                <p className="text-[9px] text-text-muted">or click to browse</p>
                            </div>
                        </button>
                    )
                ) : (
                    /* Audio Tab */
                    audioFile ? (
                        <div className="flex flex-col gap-3 p-2">
                            <div className="flex items-center gap-3 p-3 rounded-lg bg-primary/10 border border-primary/20">
                                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                                    <Music size={16} className="text-primary" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-xs font-medium text-text-primary truncate">
                                        {audioFile.name}
                                    </p>
                                    <p className="text-[10px] text-text-muted">
                                        {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                                    </p>
                                </div>
                            </div>
                            {onAudioRemove && (
                                <button
                                    onClick={onAudioRemove}
                                    className="w-full py-2 text-[10px] font-medium text-red-400 bg-red-500/10 rounded-lg hover:bg-red-500/20 transition-colors"
                                >
                                    Remove & Replace
                                </button>
                            )}
                        </div>
                    ) : (
                        <button
                            onClick={onAudioUpload}
                            className="w-full h-full min-h-[100px] flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-white/10 text-text-muted hover:border-primary/50 hover:text-primary transition-all"
                        >
                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                                <Music size={16} />
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] font-semibold">Drop audio</p>
                                <p className="text-[9px] text-text-muted">MP3, WAV, M4A</p>
                            </div>
                        </button>
                    )
                )}
            </div>
        </Card>
    );
}
