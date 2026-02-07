import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type ViewMode = 'reel' | 'podcast' | 'home' | 'history';
type Theme = 'dark' | 'light' | 'midnight' | 'nord' | 'sunset';

interface AppContextType {
    viewMode: ViewMode;
    setViewMode: (mode: ViewMode) => void;
    jobId: string | null;
    setJobId: (id: string | null) => void;
    theme: Theme;
    setTheme: (theme: Theme) => void;
    toggleTheme: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
    const [viewMode, setViewMode] = useState<ViewMode>('reel');
    const [jobId, setJobId] = useState<string | null>(null);
    const [theme, setTheme] = useState<Theme>(() => {
        const stored = localStorage.getItem('app-theme') as Theme;
        return stored || 'dark';
    });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('app-theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        const nextTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(nextTheme);
    };

    const value = {
        viewMode,
        setViewMode,
        jobId,
        setJobId,
        theme,
        setTheme,
        toggleTheme,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
}
