import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../ui/utils';

interface FeatureCardProps {
    icon: React.ReactNode;
    title: string;
    description: string;
    selected: boolean;
    onClick: () => void;
    color: string;
    children?: React.ReactNode;
}

export default function FeatureCard({ icon, title, description, selected, onClick, color, children }: FeatureCardProps) {
    return (
        <motion.div
            whileHover={{ y: -4 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClick}
            className={cn(
                "relative p-5 rounded-2xl border-2 transition-all cursor-pointer overflow-hidden group",
                selected
                    ? `bg-gradient-to-br from-${color}/10 to-transparent border-${color} shadow-[0_0_20px_rgba(var(--${color}-rgb),0.15)]`
                    : "bg-surface border-border hover:border-text-muted"
            )}
        >
            <div className="relative z-10 flex gap-4">
                <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-500",
                    selected ? `bg-${color}/20 text-${color}` : "bg-surface-elevated text-text-muted group-hover:text-text-secondary"
                )}>
                    {icon}
                </div>
                <div className="flex-1 min-w-0">
                    <h4 className={cn("font-bold text-sm transition-colors", selected ? "text-text-primary" : "text-text-secondary")}>
                        {title}
                    </h4>
                    <p className="text-[10px] text-text-muted leading-relaxed mt-1">
                        {description}
                    </p>
                    {children}
                </div>
                <div className={cn(
                    "w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all",
                    selected ? `bg-${color} border-${color}` : "border-border"
                )}>
                    {selected && <div className="w-2 h-2 rounded-full bg-canvas" />}
                </div>
            </div>

            {/* Animated Glow Background */}
            {selected && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className={cn("absolute -bottom-8 -right-8 w-24 h-24 blur-3xl rounded-full opacity-20", `bg-${color}`)}
                />
            )}
        </motion.div>
    );
}
