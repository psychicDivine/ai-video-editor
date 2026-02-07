import React, { useState } from 'react';
import { Maximize2, Monitor, Smartphone, Gauge, Layout } from 'lucide-react';
import { cn } from '../../ui/utils';
import Button from '../../ui/Button';
import Card from '../../ui/Card';

interface PreviewPanelProps {
    videoRef: React.RefObject<HTMLVideoElement>;
    hoveredClipUrl: string | null;
}

export default function PreviewPanel({ videoRef, hoveredClipUrl }: PreviewPanelProps) {
    const [aspect, setAspect] = useState<'9:16' | '16:9'>('9:16');
    const [lens, setLens] = useState<'fit' | 'fill'>('fill');
    const [showGuides, setShowGuides] = useState(true);
    const [zoom, setZoom] = useState(1);

    // Responsive sizing - fill available space

    return (
        <Card variant="glass" padding="none" className="h-full flex flex-col relative group/workspace">
            {/* Global Workspace Noise */}
            <div className="absolute inset-0 bg-noise opacity-[0.03] pointer-events-none" />

            <div className="p-3 border-b border-white/5 flex items-center justify-between bg-canvas/40 relative z-20">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <Monitor className="w-4 h-4 text-reel" />
                        <span className="text-[10px] font-black text-text-muted uppercase tracking-[0.2em]">Master Preview Deck</span>
                    </div>
                </div>
                <div className="flex gap-1.5 bg-canvas p-1 rounded-xl border border-white/10">
                    <button
                        onClick={() => setAspect('9:16')}
                        className={cn(
                            "flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-[10px] font-bold uppercase",
                            aspect === '9:16' ? "bg-reel/20 text-reel shadow-lg shadow-reel/10" : "text-text-muted hover:text-text-secondary"
                        )}
                    >
                        <Smartphone className="w-3.5 h-3.5" />
                        Portrait
                    </button>
                    <button
                        onClick={() => setAspect('16:9')}
                        className={cn(
                            "flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-[10px] font-bold uppercase",
                            aspect === '16:9' ? "bg-reel/20 text-reel shadow-lg shadow-reel/10" : "text-text-muted hover:text-text-secondary"
                        )}
                    >
                        <Monitor className="w-3.5 h-3.5" />
                        Cinema
                    </button>
                </div>
            </div>

            <div className="flex-1 bg-canvas relative flex items-center justify-center p-2 overflow-hidden">
                {/* Minimal Corner Brackets - only show when no video */}
                {!hoveredClipUrl && (
                    <div className="absolute inset-4 pointer-events-none z-10 rounded-xl overflow-hidden">
                        <div className="absolute top-0 left-0 w-6 h-6 border-t border-l border-reel/30 rounded-tl-lg" />
                        <div className="absolute top-0 right-0 w-6 h-6 border-t border-r border-reel/30 rounded-tr-lg" />
                        <div className="absolute bottom-0 left-0 w-6 h-6 border-b border-l border-reel/30 rounded-bl-lg" />
                        <div className="absolute bottom-0 right-0 w-6 h-6 border-b border-r border-reel/30 rounded-br-lg" />
                    </div>
                )}

                {/* Compact Status Bar - Top */}
                <div className="absolute top-2 left-2 right-2 flex justify-between items-start pointer-events-none z-20">
                    <div className="flex items-center gap-2 bg-black/60 backdrop-blur-sm px-2 py-1 rounded-lg">
                        <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                        <span className="text-[9px] font-mono font-bold text-white/80 uppercase">Live</span>
                    </div>
                    {hoveredClipUrl && (
                        <div className="bg-black/60 backdrop-blur-sm px-2 py-1 rounded-lg">
                            <span className="text-[9px] font-mono font-bold text-reel">4K • 23.976fps</span>
                        </div>
                    )}
                </div>

                <div
                    className={cn(
                        "relative bg-black shadow-2xl transition-all duration-300 overflow-hidden border border-white/5 mx-auto flex items-center justify-center",
                        aspect === '9:16' ? "aspect-[9/16] h-full max-h-full" : "aspect-video w-full max-w-full"
                    )}
                >
                    {/* Background Blur */}
                    {hoveredClipUrl && (
                        <video
                            src={hoveredClipUrl}
                            className="absolute inset-0 w-full h-full object-cover blur-3xl opacity-30 scale-125"
                            muted
                            playsInline
                        />
                    )}

                    <video
                        ref={videoRef}
                        src={hoveredClipUrl || undefined}
                        className={cn(
                            "relative z-10 transition-all duration-500",
                            lens === 'fill'
                                ? (aspect === '9:16' ? "h-full w-auto max-h-full object-contain" : "w-full h-full object-cover")
                                : "max-w-full max-h-full object-contain"
                        )}
                        style={{ transform: `scale(${zoom})` }}
                        playsInline
                        muted
                        loop
                        autoPlay
                    />

                    {/* Safe Zone Guides - Simplified */}
                    {showGuides && aspect === '9:16' && hoveredClipUrl && (
                        <div className="absolute inset-0 pointer-events-none z-20">
                            <div className="absolute inset-[10%] border border-white/10 border-dashed" />
                            <div className="absolute inset-0 flex items-center justify-center opacity-30">
                                <div className="w-px h-8 bg-white" />
                                <div className="h-px w-8 bg-white absolute" />
                            </div>
                        </div>
                    )}

                    {/* Smart Reframe Zone */}
                    {hoveredClipUrl && aspect === '16:9' && (
                        <div className="absolute z-20 top-0 left-1/2 -translate-x-1/2 h-full aspect-[9/16] border-2 border-reel border-dashed shadow-[0_0_50px_rgba(0,240,255,0.2)] flex items-center justify-center">
                            <div className="text-[8px] font-black text-reel uppercase tracking-widest bg-canvas px-2 py-1 rounded">Smart Reframe Zone</div>
                        </div>
                    )}

                    {!hoveredClipUrl && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0a0c10]">
                            <div className="absolute inset-0 opacity-5 bg-[linear-gradient(rgba(0,240,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,240,255,0.1)_1px,transparent_1px)] bg-[size:32px_32px]" />
                            
                            <div className="relative z-10 flex flex-col items-center gap-4">
                                <div className="w-16 h-16 rounded-full border border-reel/30 flex items-center justify-center">
                                    <Monitor className="w-7 h-7 text-reel/60" />
                                </div>
                                <div className="flex flex-col items-center gap-1">
                                    <span className="text-[10px] font-bold text-reel/80 uppercase tracking-widest">No Preview</span>
                                    <span className="text-[9px] text-text-muted">Hover a clip to preview</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Floating Overlay Controls - Center Bottom */}
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1.5 bg-black/90 backdrop-blur-xl px-2 py-1.5 rounded-xl border border-white/10 shadow-2xl z-40">
                    <div className="flex items-center bg-white/5 rounded-xl p-1 gap-1">
                        <Button
                            variant="ghost"
                            size="icon"
                            className={cn("w-8 h-8 rounded-lg", lens === 'fill' ? "bg-reel/20 text-reel" : "text-text-muted")}
                            onClick={() => setLens('fill')}
                        >
                            <Layout className="w-4 h-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            className={cn("w-8 h-8 rounded-lg", lens === 'fit' ? "bg-reel/20 text-reel" : "text-text-muted")}
                            onClick={() => setLens('fit')}
                        >
                            <Maximize2 className="w-4 h-4" />
                        </Button>
                    </div>

                    <div className="h-4 w-px bg-white/10 mx-2" />

                    <Button variant="ghost" size="icon" onClick={() => setShowGuides(!showGuides)} className="w-8 h-8">
                        <div className={cn("w-2 h-2 rounded-full transition-all duration-500", showGuides ? "bg-reel shadow-[0_0_8px_#00F0FF]" : "bg-text-muted")} />
                    </Button>

                    <div className="h-4 w-px bg-white/10 mx-2" />

                    <div className="flex items-center gap-2 px-3">
                        <Gauge className="w-3.5 h-3.5 text-reel animate-pulse" />
                        <span className="text-[9px] font-mono font-bold text-reel uppercase w-8 text-center">{Math.round(zoom * 100)}%</span>
                        <input
                            type="range"
                            min="0.3"
                            max="2"
                            step="0.1"
                            value={zoom}
                            onChange={(e) => setZoom(parseFloat(e.target.value))}
                            className="w-16 h-1 bg-white/20 rounded-lg appearance-none cursor-pointer accent-reel relative z-20 pointer-events-auto"
                        />
                    </div>
                </div>
            </div>
        </Card>
    );
}
