import { useState, useRef, useEffect } from 'react';
import { User, Settings, LogOut, Palette, Check } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { cn } from '../../ui/utils';

type Theme = 'dark' | 'light' | 'midnight' | 'nord' | 'sunset';

const themes: { id: Theme; name: string; description: string; preview: string }[] = [
    { id: 'dark', name: 'Dark', description: 'Professional dark theme', preview: 'bg-gradient-to-br from-slate-900 to-slate-800' },
    { id: 'light', name: 'Light', description: 'Clean light theme', preview: 'bg-gradient-to-br from-white to-slate-100' },
    { id: 'midnight', name: 'Midnight', description: 'Pure black OLED theme', preview: 'bg-gradient-to-br from-black to-slate-950' },
    { id: 'nord', name: 'Nord', description: 'Arctic inspired palette', preview: 'bg-gradient-to-br from-[#2e3440] to-[#3b4252]' },
    { id: 'sunset', name: 'Sunset', description: 'Warm evening vibes', preview: 'bg-gradient-to-br from-[#1a0a0f] via-[#2d1b24] to-[#3d2831]' },
];

export default function ProfileMenu() {
    const [isOpen, setIsOpen] = useState(false);
    const [showThemes, setShowThemes] = useState(false);
    const { theme, setTheme } = useApp();
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                setShowThemes(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    const handleThemeChange = (newTheme: Theme) => {
        setTheme(newTheme);
        setShowThemes(false);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={menuRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 border-2 border-border shadow-lg hover:scale-105 transition-transform"
            />

            {isOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-surface border border-border rounded-2xl shadow-xl overflow-hidden z-50">
                    {!showThemes ? (
                        <>
                            {/* User Info */}
                            <div className="p-4 border-b border-border bg-surface-elevated">
                                <div className="flex items-center gap-3">
                                    <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                                        <User className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="font-bold text-sm text-text-primary">Studio User</h3>
                                        <p className="text-xs text-text-muted">user@studio.ai</p>
                                    </div>
                                </div>
                            </div>

                            {/* Menu Items */}
                            <div className="p-2">
                                <button
                                    onClick={() => setShowThemes(true)}
                                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-elevated transition-colors text-left group"
                                >
                                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                        <Palette className="w-4 h-4 text-primary" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-text-primary">Appearance</p>
                                        <p className="text-xs text-text-muted capitalize">{theme} theme</p>
                                    </div>
                                </button>

                                <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-elevated transition-colors text-left group">
                                    <div className="w-8 h-8 rounded-lg bg-text-muted/10 flex items-center justify-center group-hover:bg-text-muted/20 transition-colors">
                                        <Settings className="w-4 h-4 text-text-secondary" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-text-primary">Settings</p>
                                        <p className="text-xs text-text-muted">Preferences & config</p>
                                    </div>
                                </button>
                            </div>

                            {/* Sign Out */}
                            <div className="p-2 border-t border-border">
                                <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-danger/10 transition-colors text-left group">
                                    <div className="w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center group-hover:bg-danger/20 transition-colors">
                                        <LogOut className="w-4 h-4 text-danger" />
                                    </div>
                                    <p className="text-sm font-medium text-danger">Sign Out</p>
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            {/* Theme Selector */}
                            <div className="p-4 border-b border-border bg-surface-elevated">
                                <button
                                    onClick={() => setShowThemes(false)}
                                    className="text-xs text-text-muted hover:text-text-primary transition-colors mb-2"
                                >
                                    ← Back
                                </button>
                                <h3 className="font-bold text-sm text-text-primary">Choose Theme</h3>
                                <p className="text-xs text-text-muted mt-1">Select your preferred color scheme</p>
                            </div>

                            <div className="p-3 max-h-96 overflow-y-auto custom-scrollbar">
                                <div className="space-y-2">
                                    {themes.map((t) => (
                                        <button
                                            key={t.id}
                                            onClick={() => handleThemeChange(t.id)}
                                            className={cn(
                                                "w-full flex items-center gap-3 p-3 rounded-xl transition-all text-left border-2",
                                                theme === t.id
                                                    ? "bg-primary/10 border-primary shadow-sm"
                                                    : "bg-transparent border-transparent hover:bg-surface-elevated"
                                            )}
                                        >
                                            <div className={cn("w-12 h-12 rounded-lg shadow-md border border-border/50", t.preview)} />
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <p className="text-sm font-bold text-text-primary">{t.name}</p>
                                                    {theme === t.id && (
                                                        <Check className="w-4 h-4 text-primary" />
                                                    )}
                                                </div>
                                                <p className="text-xs text-text-muted">{t.description}</p>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
