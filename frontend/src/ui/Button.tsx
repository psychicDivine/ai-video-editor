import * as React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "./utils";

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "children"> {
    variant?: "primary" | "secondary" | "ghost" | "glass" | "reel" | "podcast";
    size?: "sm" | "md" | "lg" | "icon";
    children?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", size = "md", ...props }, ref) => {
        const variants = {
            primary: "bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20",
            secondary: "bg-surface-elevated text-text-primary hover:bg-surface-elevated/80 border border-border",
            ghost: "bg-transparent text-text-secondary hover:text-text-primary hover:bg-surface-elevated/40",
            glass: "bg-surface/30 backdrop-blur-md border border-border text-text-primary hover:bg-surface/50 shadow-sm",
            reel: "bg-reel/10 text-reel border border-reel/30 hover:bg-reel hover:text-white dark:hover:text-canvas hover:shadow-neon-reel",
            podcast: "bg-podcast/10 text-podcast border border-podcast/30 hover:bg-podcast hover:text-white dark:hover:text-canvas hover:shadow-neon-podcast",
        };

        const sizes = {
            sm: "px-3 py-1.5 text-xs",
            md: "px-5 py-2.5 text-sm font-semibold",
            lg: "px-8 py-4 text-base font-bold tracking-widest uppercase",
            icon: "p-2.5",
        };

        return (
            <motion.button
                ref={ref}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                    "inline-flex items-center justify-center rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed outline-none focus:ring-2 focus:ring-primary/40",
                    variants[variant],
                    sizes[size],
                    className
                )}
                {...props}
            />
        );
    }
);

Button.displayName = "Button";

export default Button;
