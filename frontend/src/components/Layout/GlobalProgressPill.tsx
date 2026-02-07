import { useEffect, useState } from 'react';
import axios from 'axios';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function GlobalProgressPill() {
    const { jobId, setJobId } = useApp();
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');

    useEffect(() => {
        if (!jobId) return;
        const poll = async () => {
            try {
                const res = await axios.get(`/api/jobs/${jobId}`);
                setProgress(res.data.progress);
                setStatus(res.data.status);
                if (res.data.status === 'COMPLETED' || res.data.status === 'FAILED') return;
                setTimeout(poll, 3000);
            } catch (e) {
                setTimeout(poll, 5000);
            }
        };
        poll();
    }, [jobId]);

    if (!jobId) return null;

    return (
        <div className="fixed bottom-8 right-8 z-50 animate-in slide-in-from-right-4 duration-500">
            <div className="bg-canvas border border-border shadow-2xl rounded-2xl px-4 py-3 flex items-center gap-4 min-w-[240px]">
                {status === 'COMPLETED' ? (
                    <CheckCircle2 className="text-green-500 w-5 h-5" />
                ) : status === 'FAILED' ? (
                    <AlertCircle className="text-red-500 w-5 h-5" />
                ) : (
                    <div className="relative flex items-center justify-center">
                        <Loader2 className="animate-spin text-primary w-5 h-5" />
                        <span className="absolute text-[8px] font-bold text-primary">{progress}%</span>
                    </div>
                )}

                <div className="flex-1">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-text-primary">AI Operation</p>
                    <p className="text-[9px] text-text-muted truncate max-w-[120px]">{status || 'Orchestrating...'}</p>
                </div>

                <button
                    onClick={() => setJobId(null)}
                    className="text-[10px] font-bold text-text-muted hover:text-text-primary transition-colors border-l border-border pl-4"
                >
                    Dismiss
                </button>
            </div>
        </div>
    );
}
