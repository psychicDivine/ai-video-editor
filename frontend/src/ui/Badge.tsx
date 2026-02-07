import * as React from "react";
import { cn } from "./utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: "primary" | "secondary" | "reel" | "podcast" | "error" | "success";
}

export default function Badge({ className, variant = "primary", ...props }: BadgeProps) {
    const variants = {
        primary: "bg-primary/10 text-primary border-primary/20",
        secondary: "bg-surface-elevated text-text-secondary border-border",
        reel: "bg-reel/10 text-reel border-reel/20",
        podcast: "bg-podcast/10 text-podcast border-podcast/20",
        error: "bg-red-500/10 text-red-500 border-red-500/20",
        success: "bg-neon-green/10 text-neon-green border-neon-green/20",
    };

    return (
        <span
            className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-mono leading-none tracking-wider uppercase transition-colors",
                variants[variant],
                className
            )}
            {...props}
        />
    );
}
