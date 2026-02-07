import React from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import GlobalProgressPill from './GlobalProgressPill';

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex h-screen bg-canvas overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                <TopBar />
                <main className="flex-1 min-h-0 overflow-hidden">
                    {children}
                </main>
                <GlobalProgressPill />
            </div>
        </div>
    );
}
