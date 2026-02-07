import { Sun, Moon, Bell, Search } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import Button from '../../ui/Button';
import ProfileMenu from './ProfileMenu';

export default function TopBar() {
    const { theme, viewMode } = useApp();

    const getTitle = () => {
        switch (viewMode) {
            case 'reel': return 'Reel Studio';
            case 'podcast': return 'Viral Lab (Podcast)';
            case 'history': return 'Project History';
            default: return 'Studio';
        }
    };

    return (
        <header className="h-20 border-b border-border bg-canvas flex items-center justify-between px-8 sticky top-0 z-40">
            <div className="flex items-center gap-4">
                <h2 className="text-xl font-display font-bold text-text-primary capitalize">{getTitle()}</h2>
                <div className="h-6 w-px bg-border mx-2" />
                <div className="flex items-center gap-1.5 bg-surface-elevated px-3 py-1.5 rounded-full border border-border">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-[10px] font-mono font-bold text-text-secondary uppercase">API Connected</span>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative group hidden md:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted transition-colors group-focus-within:text-primary" />
                    <input
                        placeholder="Search projects..."
                        className="h-10 w-64 bg-surface-elevated border border-border rounded-xl pl-10 pr-4 text-xs text-text-primary placeholder:text-text-muted focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all outline-none"
                    />
                </div>

                <Button variant="ghost" size="icon" className="rounded-full relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-canvas" />
                </Button>

                <ProfileMenu />
            </div>
        </header>
    );
}
