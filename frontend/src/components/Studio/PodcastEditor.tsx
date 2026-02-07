import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Youtube, Upload, Sparkles, Wand2, Languages, Layout, Loader2, Music, Video, Link } from 'lucide-react';
import { motion } from 'framer-motion';
import Button from '../../ui/Button';
import Card from '../../ui/Card';
import Input from '../../ui/Input';
import Badge from '../../ui/Badge';
import { cn } from '../../ui/utils';
import FeatureCard from '../Podcast/FeatureCard';
import CaptionStyleSelector from '../CaptionStyleSelector';

interface PodcastEditorProps {
    onJobCreated: (jobId: string) => void;
}

export default function PodcastEditor({ onJobCreated }: PodcastEditorProps) {
    const [tab, setTab] = useState<'upload' | 'youtube'>('youtube');
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [ytInfo, setYtInfo] = useState<any>(null);
    const [smartReels, setSmartReels] = useState(true);
    const [captionStyle, setCaptionStyle] = useState('tiktok');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [audio, setAudio] = useState<File | null>(null);
    const [video, setVideo] = useState<File | null>(null);

    useEffect(() => {
        const fetchInfo = async () => {
            if (youtubeUrl.includes('youtube.com/') || youtubeUrl.includes('youtu.be/')) {
                try {
                    const resp = await axios.post('/api/youtube/info', { url: youtubeUrl });
                    setYtInfo(resp.data);
                } catch (err) {
                    setYtInfo(null);
                } finally {
                    // setFetchingInfo(false);
                }
            } else {
                setYtInfo(null);
            }
        };
        const timer = setTimeout(fetchInfo, 800);
        return () => clearTimeout(timer);
    }, [youtubeUrl]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            if (tab === 'youtube') {
                const resp = await axios.post('/api/youtube/download', {
                    url: youtubeUrl,
                    enable_smart_reels: smartReels,
                    caption_style: captionStyle
                });
                onJobCreated(resp.data.job_id);
            } else {
                const fd = new FormData();
                if (audio) fd.append('audio', audio);
                if (video) fd.append('video', video);
                fd.append('enable_smart_reels', String(smartReels));
                fd.append('caption_style', captionStyle);
                const resp = await axios.post('/api/podcast', fd);
                onJobCreated(resp.data.job_id);
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-12 max-w-5xl mx-auto">
            {/* Source Selection Hero */}
            <div className="flex flex-col items-center text-center mb-12">
                <Badge variant="podcast" className="mb-4">Intelligence Input</Badge>
                <h2 className="text-3xl font-display font-black text-white tracking-tighter">Choose your <span className="text-podcast italic">Viral Source</span></h2>
                <p className="text-text-secondary text-sm mt-2 max-w-lg">Our AI logic works with any medium. Paste a URL or drop your raw master files to begin the extraction.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <Card
                    variant={tab === 'youtube' ? 'glass' : 'outline'}
                    onClick={() => setTab('youtube')}
                    className={cn(
                        "p-10 group cursor-pointer relative overflow-hidden transition-all duration-500",
                        tab === 'youtube' ? "border-red-500/40 bg-red-500/5 shadow-2xl" : "hover:border-red-500/20"
                    )}
                >
                    <div className="relative z-10">
                        <div className={cn(
                            "w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-700",
                            tab === 'youtube' ? "bg-red-500 text-white shadow-[0_0_30px_rgba(239,68,68,0.4)] rotate-3" : "bg-surface-elevated text-text-muted group-hover:text-red-500 group-hover:scale-110"
                        )}>
                            <Youtube className="w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-bold text-text-primary">Global Link Discovery</h3>
                        <p className="text-xs text-text-muted mt-2 leading-relaxed">Extract high-fidelity data from any public YouTube endpoint.</p>
                    </div>
                    {tab === 'youtube' && (
                        <motion.div layoutId="src-check" className="absolute top-6 right-6 w-3 h-3 rounded-full bg-red-500 shadow-[0_0_15px_red]" />
                    )}
                </Card>

                <Card
                    variant={tab === 'upload' ? 'glass' : 'outline'}
                    onClick={() => setTab('upload')}
                    className={cn(
                        "p-10 group cursor-pointer relative overflow-hidden transition-all duration-500",
                        tab === 'upload' ? "border-primary/40 bg-primary/5 shadow-2xl" : "hover:border-primary/20"
                    )}
                >
                    <div className="relative z-10">
                        <div className={cn(
                            "w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-700",
                            tab === 'upload' ? "bg-primary text-white shadow-[0_0_30px_rgba(59,130,246,0.4)] -rotate-3" : "bg-surface-elevated text-text-muted group-hover:text-primary group-hover:scale-110"
                        )}>
                            <Upload className="w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-bold text-text-primary">Native Binary Upload</h3>
                        <p className="text-xs text-text-muted mt-2 leading-relaxed">Direct pipeline for Pro-Res, MOV, and high-bitrate MP4 assets.</p>
                    </div>
                    {tab === 'upload' && (
                        <motion.div layoutId="src-check" className="absolute top-6 right-6 w-3 h-3 rounded-full bg-primary shadow-[0_0_15px_#3b82f6]" />
                    )}
                </Card>
            </div>

            {/* Dynamic Input Area */}
            <div className="min-h-[160px] animate-in slide-in-from-bottom-4 duration-500">
                {tab === 'youtube' ? (
                    <div className="space-y-6">
                        <div className="relative group/input">
                            <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-podcast/20 rounded-2xl blur opacity-0 group-focus-within/input:opacity-100 transition-opacity" />
                            <Input
                                icon={<Link className="w-5 h-5" />}
                                placeholder="https://youtube.com/watch?v=..."
                                value={youtubeUrl}
                                onChange={(e) => setYoutubeUrl(e.target.value)}
                                className="h-20 text-xl border-2 bg-surface/80 backdrop-blur-md relative z-10"
                                label="Source Endpoint"
                            />
                        </div>

                        {ytInfo && (
                            <div className="bg-surface-elevated p-5 rounded-3xl border border-white/5 flex gap-6 animate-in zoom-in-95 duration-500 shadow-2xl">
                                <div className="relative">
                                    <img src={ytInfo.thumbnail} className="w-44 aspect-video object-cover rounded-2xl shadow-2xl border border-white/10" alt="yt" />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent rounded-2xl" />
                                </div>
                                <div className="flex-1 min-w-0 py-2">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Badge variant="reel">Target Acquired</Badge>
                                        <span className="text-[10px] font-mono text-text-muted uppercase tracking-widest">Metadata Sync OK</span>
                                    </div>
                                    <h4 className="text-lg font-bold text-text-primary truncate">{ytInfo.title}</h4>
                                    <div className="flex gap-6 mt-3 text-[10px] font-mono text-text-secondary uppercase">
                                        <span className="flex items-center gap-2 px-2 py-1 bg-black/20 rounded-lg"><Youtube size={12} className="text-red-500" /> {ytInfo.uploader}</span>
                                        <span className="flex items-center gap-2 px-2 py-1 bg-black/20 rounded-lg">TIME: {Math.floor(ytInfo.duration / 60)}m {ytInfo.duration % 60}s</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-6">
                        <Card
                            variant="outline"
                            className="p-10 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-primary/5 hover:border-primary/40 transition-all duration-300 relative border-dashed"
                        >
                            <input type="file" accept="audio/*" onChange={e => setAudio(e.target.files?.[0] || null)} className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                            <div className="w-16 h-16 rounded-full bg-surface-elevated flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Music className="w-8 h-8 text-text-muted group-hover:text-primary transition-colors" />
                            </div>
                            <p className="text-sm font-bold text-text-primary">{audio ? audio.name : 'Master Audio'}</p>
                            <p className="text-[10px] text-text-muted mt-2 uppercase font-mono tracking-[0.2em]">{audio ? (audio.size / 1024 / 1024).toFixed(1) + 'MB' : 'Lossless WAV / MP3'}</p>
                            {audio && <div className="absolute top-4 right-4 w-2 h-2 bg-primary rounded-full animate-ping" />}
                        </Card>
                        <Card
                            variant="outline"
                            className="p-10 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-reel/5 hover:border-reel/40 transition-all duration-300 relative border-dashed"
                        >
                            <input type="file" accept="video/*" onChange={e => setVideo(e.target.files?.[0] || null)} className="absolute inset-0 opacity-0 cursor-pointer z-10" />
                            <div className="w-16 h-16 rounded-full bg-surface-elevated flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <Video className="w-8 h-8 text-text-muted group-hover:text-reel transition-colors" />
                            </div>
                            <p className="text-sm font-bold text-text-primary">{video ? video.name : 'Video Reference'}</p>
                            <p className="text-[10px] text-text-muted mt-2 uppercase font-mono tracking-[0.2em]">{video ? (video.size / 1024 / 1024).toFixed(1) + 'MB' : '4K / 1080P Container'}</p>
                            {video && <div className="absolute top-4 right-4 w-2 h-2 bg-reel rounded-full animate-ping" />}
                        </Card>
                    </div>
                )}
            </div>

            {/* AI Intelligence Config */}
            <section className="space-y-6 pt-6 border-t border-white/5">
                <header className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-podcast/10 rounded-lg">
                            <Sparkles className="text-podcast w-5 h-5 animate-pulse" />
                        </div>
                        <div>
                            <h3 className="text-sm font-black uppercase tracking-[0.2em] text-text-primary">Viral Intelligence Suite</h3>
                            <p className="text-[10px] text-text-muted">Select analysis modules to process your source</p>
                        </div>
                    </div>
                    <div className="px-3 py-1 bg-podcast/5 border border-podcast/20 rounded-full">
                        <span className="text-[10px] font-mono font-bold text-podcast uppercase">Logic Mode: Gemini 1.5 Flash</span>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <FeatureCard
                        icon={<Wand2 />}
                        title="Moment Detection"
                        description="Our AI scans for high-energy hooks and narrative peaks."
                        selected={smartReels}
                        onClick={() => setSmartReels(!smartReels)}
                        color="podcast"
                    >
                        <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[8px] font-mono text-text-muted uppercase">Virality Prediction</span>
                            <Badge variant="podcast" className="text-[9px] px-1.5 py-0.5">98% Match</Badge>
                        </div>
                    </FeatureCard>
                    <FeatureCard
                        icon={<Languages />}
                        title="Lexical Extraction"
                        description="Whisper-powered word-level transcription and styling."
                        selected={true}
                        onClick={() => { }}
                        color="primary"
                    >
                        <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[8px] font-mono text-text-muted uppercase">Logic Engine</span>
                            <span className="text-[9px] font-mono text-primary font-bold">Whisper v3-Large</span>
                        </div>
                    </FeatureCard>
                    <FeatureCard
                        icon={<Layout />}
                        title="Visual Re-mapping"
                        description="Auto logic for speaker tracking and vertical cropping."
                        selected={true}
                        onClick={() => { }}
                        color="reel"
                    >
                        <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[8px] font-mono text-text-muted uppercase">Auto-Reframe</span>
                            <div className="flex items-center gap-1.5">
                                <div className="w-1 h-1 rounded-full bg-reel animate-pulse" />
                                <span className="text-[9px] font-mono text-reel font-bold">Smart-Crop On</span>
                            </div>
                        </div>
                    </FeatureCard>
                </div>
            </section>

            {/* Caption Preview Section */}
            <section className="bg-surface/50 p-6 rounded-3xl border border-border">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold text-text-primary">Caption Visualization</h3>
                    <p className="text-[10px] text-text-muted uppercase font-mono">Real-time Apply</p>
                </div>
                <CaptionStyleSelector selectedStyle={captionStyle} onStyleChange={setCaptionStyle} />
            </section>

            {/* Final Action */}
            <div className="flex flex-col items-center pt-8 border-t border-white/5 pb-20">
                {error && (
                    <div className="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-2xl flex items-center gap-3 animate-in shake-1">
                        <div className="w-2 h-2 rounded-full bg-danger animate-pulse" />
                        <p className="text-[11px] font-bold text-danger uppercase tracking-wide">Orchestration Error: {error}</p>
                    </div>
                )}

                <Button
                    variant="podcast"
                    size="lg"
                    className="h-24 px-16 group relative overflow-hidden shadow-[0_20px_50px_rgba(176,38,255,0.2)] rounded-3xl"
                    onClick={handleSubmit}
                    disabled={loading || (tab === 'youtube' && !youtubeUrl) || (tab === 'upload' && !audio)}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-podcast via-primary to-podcast opacity-0 group-hover:opacity-20 transition-all duration-700 animate-shimmer" />
                    <span className="relative z-10 flex flex-col items-center">
                        <span className="text-[10px] font-black uppercase tracking-[0.5em] mb-1 opacity-60">Initialize Viral Loop</span>
                        <span className="text-xl font-display font-black flex items-center gap-3">
                            {loading ? <Loader2 className="animate-spin" /> : <Sparkles className="group-hover:rotate-12 transition-transform" />}
                            {loading ? 'Synthesizing Pipeline...' : 'Generate Viral Reels'}
                        </span>
                    </span>
                </Button>
                <p className="text-[9px] text-text-muted mt-6 uppercase tracking-[0.3em] font-bold">Encrypted Processing • Pro-Res Output • AI Driven</p>
            </div>
        </div>
    );
}
