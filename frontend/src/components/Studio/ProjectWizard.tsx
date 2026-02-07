import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Music, Film, Play } from 'lucide-react';
import Button from '../../ui/Button';
import Card from '../../ui/Card';
import { cn } from '../../ui/utils';
import { brandName } from '../../config/brand';

interface ProjectWizardProps {
    onComplete: (videos: File[], audio: File) => void;
    onSkip?: () => void;
}

export default function ProjectWizard({ onComplete, onSkip }: ProjectWizardProps) {
    const [videoFiles, setVideoFiles] = useState<File[]>([]);
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState<'audio' | 'video' | null>(null);

    const videoInputRef = useRef<HTMLInputElement>(null);
    const audioInputRef = useRef<HTMLInputElement>(null);
    const videoDropRef = useRef<HTMLDivElement>(null);
    const audioDropRef = useRef<HTMLDivElement>(null);

    const isReady = videoFiles.length > 0 && audioFile !== null;

    // Handle drag events
    const handleDrag = (e: React.DragEvent, zone: 'audio' | 'video') => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(zone);
        } else if (e.type === 'dragleave') {
            setDragActive(null);
        }
    };

    // Handle drop events
    const handleDrop = (e: React.DragEvent, zone: 'audio' | 'video') => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(null);

        const files = Array.from(e.dataTransfer.files);

        if (zone === 'audio') {
            const audio = files.find((f) => f.type.startsWith('audio/'));
            if (audio) setAudioFile(audio);
        } else if (zone === 'video') {
            const videos = files.filter((f) => f.type.startsWith('video/'));
            setVideoFiles((prev) => [...prev, ...videos].slice(0, 15)); // Max 15 clips
        }
    };

    // Handle file input change
    const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files);
            setVideoFiles((prev) => [...prev, ...files].slice(0, 15));
        }
    };

    const handleAudioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setAudioFile(e.target.files[0]);
        }
    };

    const removeVideoFile = (index: number) => {
        setVideoFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const removeAudioFile = () => {
        setAudioFile(null);
    };

    const handleStart = () => {
        if (isReady) {
            onComplete(videoFiles, audioFile!);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop blur */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            />

            {/* Modal container */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden"
            >
                <Card variant="default" padding="lg" className="flex flex-col h-full">
                    {/* Header */}
                    <div className="mb-8 text-center">
                        <h1 className="text-4xl font-bold text-text-primary mb-2">
                            Start Your Reel
                        </h1>
                        <p className="text-text-secondary text-sm">
                            Upload footage and select a soundtrack to begin
                        </p>
                    </div>

                    {/* Main Grid */}
                    <div className="grid grid-cols-2 gap-8 flex-1 min-h-0">
                        {/* Audio Drop Zone */}
                        <div
                            ref={audioDropRef}
                            onDragEnter={(e) => handleDrag(e, 'audio')}
                            onDragLeave={(e) => handleDrag(e, 'audio')}
                            onDragOver={(e) => handleDrag(e, 'audio')}
                            onDrop={(e) => handleDrop(e, 'audio')}
                            onClick={() => audioInputRef.current?.click()}
                            className={cn(
                                'relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-300 p-6 group',
                                dragActive === 'audio'
                                    ? 'border-primary bg-primary/10 scale-105'
                                    : 'border-border hover:border-primary/50 hover:bg-primary/5'
                            )}
                        >
                            <input
                                ref={audioInputRef}
                                type="file"
                                accept="audio/*"
                                onChange={handleAudioChange}
                                className="hidden"
                            />

                            {audioFile ? (
                                <>
                                    <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4 group-hover:bg-primary/30 transition-colors">
                                        <Music className="w-8 h-8 text-primary" />
                                    </div>
                                    <p className="font-semibold text-text-primary text-center break-all">
                                        {audioFile.name}
                                    </p>
                                    <p className="text-xs text-text-secondary mt-1">
                                        {(audioFile.size / (1024 * 1024)).toFixed(2)} MB
                                    </p>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            removeAudioFile();
                                        }}
                                        className="mt-4 px-3 py-1 text-xs bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/40 transition-colors"
                                    >
                                        Remove
                                    </button>
                                </>
                            ) : (
                                <>
                                    <div className="flex items-center justify-center w-16 h-16 rounded-full bg-surface-elevated mb-4 group-hover:bg-primary/20 transition-colors">
                                        <Music className="w-8 h-8 text-text-secondary group-hover:text-primary" />
                                    </div>
                                    <p className="font-semibold text-text-primary text-center">
                                        Master Soundtrack
                                    </p>
                                    <p className="text-xs text-text-secondary mt-2 text-center">
                                        Drop your audio track here
                                    </p>
                                    <p className="text-[10px] text-text-muted mt-3 font-mono">
                                        Required
                                    </p>
                                </>
                            )}
                        </div>

                        {/* Video Drop Zone */}
                        <div
                            ref={videoDropRef}
                            onDragEnter={(e) => handleDrag(e, 'video')}
                            onDragLeave={(e) => handleDrag(e, 'video')}
                            onDragOver={(e) => handleDrag(e, 'video')}
                            onDrop={(e) => handleDrop(e, 'video')}
                            onClick={() => videoInputRef.current?.click()}
                            className={cn(
                                'relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed cursor-pointer transition-all duration-300 p-6 group overflow-auto',
                                dragActive === 'video'
                                    ? 'border-reel bg-reel/10 scale-105'
                                    : 'border-border hover:border-reel/50 hover:bg-reel/5'
                            )}
                        >
                            <input
                                ref={videoInputRef}
                                type="file"
                                accept="video/*"
                                multiple
                                onChange={handleVideoChange}
                                className="hidden"
                            />

                            {videoFiles.length > 0 ? (
                                <>
                                    <div className="w-full mb-4">
                                        <p className="text-sm font-semibold text-text-primary mb-3">
                                            {videoFiles.length} clip{videoFiles.length !== 1 ? 's' : ''} selected
                                        </p>
                                        <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto custom-scrollbar">
                                            {videoFiles.map((file, index) => (
                                                <div
                                                    key={index}
                                                    className="flex items-center justify-between bg-surface-elevated rounded-lg p-2 text-xs"
                                                >
                                                    <span className="truncate text-text-secondary flex-1">
                                                        {file.name}
                                                    </span>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            removeVideoFile(index);
                                                        }}
                                                        className="ml-2 p-0.5 text-red-400 hover:bg-red-500/20 rounded transition-colors"
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            videoInputRef.current?.click();
                                        }}
                                        className="mt-4 px-3 py-1 text-xs bg-reel/20 text-reel rounded-lg hover:bg-reel/40 transition-colors"
                                    >
                                        Add More
                                    </button>
                                </>
                            ) : (
                                <>
                                    <div className="flex items-center justify-center w-16 h-16 rounded-full bg-surface-elevated mb-4 group-hover:bg-reel/20 transition-colors">
                                        <Film className="w-8 h-8 text-text-secondary group-hover:text-reel" />
                                    </div>
                                    <p className="font-semibold text-text-primary text-center">
                                        Video Footage
                                    </p>
                                    <p className="text-xs text-text-secondary mt-2 text-center">
                                        Drop your video clips here
                                    </p>
                                    <p className="text-[10px] text-text-muted mt-3 font-mono">
                                        Up to 15 clips
                                    </p>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="mt-8 flex items-center justify-between pt-6 border-t border-border">
                        <button
                            onClick={onSkip}
                            className="text-xs text-text-secondary hover:text-text-primary transition-colors"
                        >
                            Skip for now
                        </button>

                        <Button
                            onClick={handleStart}
                            disabled={!isReady}
                            variant="primary"
                            size="lg"
                            className="flex items-center gap-2"
                        >
                            <Play className="w-4 h-4" />
                            {brandName}
                        </Button>
                    </div>
                </Card>
            </motion.div>
        </div>
    );
}
