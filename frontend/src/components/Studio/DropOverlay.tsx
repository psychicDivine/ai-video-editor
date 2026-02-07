import React from 'react';
import { Film, Music, Upload } from 'lucide-react';
import { cn } from '../../ui/utils';

interface DropOverlayProps {
    visible: boolean;
    dragType: 'video' | 'audio' | 'mixed' | null;
}

export default function DropOverlay({ visible, dragType }: DropOverlayProps) {
    if (!visible) return null;

    return (
        <div className="absolute inset-0 z-50 bg-canvas/90 backdrop-blur-sm flex items-center justify-center p-8 animate-in fade-in duration-200">
            {dragType === 'video' ? (
                // Video-only zone
                <DropZone
                    icon={Film}
                    title="Drop Video Files"
                    subtitle="Add up to 15 clips • MP4, MOV, WebM"
                    color="reel"
                    active
                    large
                />
            ) : dragType === 'audio' ? (
                // Audio-only zone
                <DropZone
                    icon={Music}
                    title="Drop Audio Track"
                    subtitle="MP3, WAV, M4A"
                    color="primary"
                    active
                    large
                />
            ) : (
                // Split zones for mixed or unknown file types
                <div className="w-full h-full grid grid-cols-2 gap-6 max-w-4xl max-h-96">
                    <DropZone
                        icon={Film}
                        title="Drop Videos"
                        subtitle="MP4, MOV, WebM"
                        color="reel"
                    />
                    <DropZone
                        icon={Music}
                        title="Drop Audio"
                        subtitle="MP3, WAV, M4A"
                        color="primary"
                    />
                </div>
            )}
        </div>
    );
}

interface DropZoneProps {
    icon: React.ElementType;
    title: string;
    subtitle: string;
    color: 'reel' | 'primary';
    active?: boolean;
    large?: boolean;
}

function DropZone({ icon: Icon, title, subtitle, color, active, large }: DropZoneProps) {
    const colorClasses = color === 'reel' 
        ? 'border-reel/50 bg-reel/5 text-reel'
        : 'border-primary/50 bg-primary/5 text-primary';

    const activeClasses = active
        ? color === 'reel'
            ? 'border-reel bg-reel/10 scale-[1.02]'
            : 'border-primary bg-primary/10 scale-[1.02]'
        : '';

    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed transition-all duration-300',
                colorClasses,
                activeClasses,
                large ? 'w-full max-w-md h-64' : 'h-full'
            )}
        >
            <div className={cn(
                'p-4 rounded-full',
                color === 'reel' ? 'bg-reel/20' : 'bg-primary/20'
            )}>
                <Icon className="w-10 h-10" />
            </div>
            <div className="text-center">
                <h3 className="text-lg font-bold text-text-primary">{title}</h3>
                <p className="text-xs text-text-secondary mt-1">{subtitle}</p>
            </div>
            <div className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium',
                color === 'reel' ? 'bg-reel/20 text-reel' : 'bg-primary/20 text-primary'
            )}>
                <Upload className="w-3.5 h-3.5" />
                Release to upload
            </div>
        </div>
    );
}
