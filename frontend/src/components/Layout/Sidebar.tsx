import { motion } from 'framer-motion';
import { Video, Mic, Clock, Settings, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { cn } from '../../ui/utils';
import { brandName, brandTagline } from '../../config/brand';

export default function Sidebar() {
    const { viewMode, setViewMode, jobId } = useApp();

    const navItems = [
        { id: 'reel', icon: Video, label: 'Reel Studio', color: 'text-reel' },
        { id: 'podcast', icon: Mic, label: 'Viral Lab', color: 'text-podcast' },
        { id: 'history', icon: Clock, label: 'Past Works', color: 'text-text-secondary' },
    ];

    return (
        <aside className="w-64 border-r border-border bg-surface flex flex-col h-screen sticky top-0 z-50">
            {/* Brand Header */}
            <div className="p-8 flex items-center gap-4">
                <div className="relative group">
                    <div className="absolute -inset-2 bg-primary/20 rounded-2xl blur-lg group-hover:bg-primary/40 transition-all duration-700 animate-pulse" />
                    <div className="relative w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-indigo-600 flex items-center justify-center shadow-2xl shadow-primary/30 transform group-hover:rotate-6 transition-transform">
                        <Sparkles className="text-white w-6 h-6 animate-float" />
                    </div>
                </div>
                <div>
                    <h1 className="font-display font-black text-xl text-text-primary tracking-tighter leading-none">
                        {brandName}
                    </h1>
                    <span className="text-[9px] font-mono text-text-muted uppercase tracking-[0.3em] block mt-1">{brandTagline}</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-8 space-y-2">
                <div className="px-4 mb-6">
                    <span className="text-[10px] font-black text-text-muted uppercase tracking-[0.25em] opacity-50">Discovery Hub</span>
                </div>

                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setViewMode(item.id as any)}
                        className={cn(
                            "w-full flex items-center justify-between px-4 py-3.5 rounded-2xl transition-all duration-300 group relative",
                            viewMode === item.id
                                ? "bg-primary/10 text-text-primary shadow-inner"
                                : "text-text-secondary hover:bg-white/5 hover:text-text-primary"
                        )}
                    >
                        <div className="flex items-center gap-3 relative z-10">
                            <item.icon className={cn(
                                "w-5 h-5 transition-transform duration-500 group-hover:scale-110",
                                viewMode === item.id ? item.color : "group-hover:text-text-primary"
                            )} />
                            <span className="text-sm font-bold tracking-tight">{item.label}</span>
                        </div>

                        {/* Status Indicators */}
                        {viewMode === item.id ? (
                            <motion.div
                                layoutId="active-nav-glow"
                                className="absolute inset-0 bg-primary/5 rounded-2xl border border-primary/20"
                            />
                        ) : null}

                        {jobId && item.id === 'reel' && (
                            <div className="relative">
                                <div className="absolute -inset-1 bg-reel/40 rounded-full blur animate-pulse" />
                                <div className="w-1.5 h-1.5 rounded-full bg-reel relative z-10 shadow-[0_0_8px_#00F0FF]" />
                            </div>
                        )}
                    </button>
                ))}
            </nav>

            {/* Footer Settings */}
            <div className="p-6 border-t border-border/50 bg-black/20">
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-white/5 text-text-secondary hover:bg-white/5 hover:text-text-primary transition-all">
                    <Settings className="w-4 h-4 opacity-60" />
                    <span className="text-xs font-bold uppercase tracking-widest">Global Params</span>
                </button>
            </div>
        </aside>
    );
}
