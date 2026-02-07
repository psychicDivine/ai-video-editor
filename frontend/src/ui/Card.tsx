import * as React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "./utils";

interface CardProps extends HTMLMotionProps<"div"> {
    variant?: "default" | "glass" | "outline";
    padding?: "none" | "sm" | "md" | "lg";
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = "default", padding = "md", ...props }, ref) => {
        const variants = {
            default: "bg-surface border border-border shadow-md dark:shadow-2xl",
            glass: "glass-panel shadow-lg dark:shadow-glass",
            outline: "bg-transparent border-2 border-border border-dashed",
        };

        const paddings = {
            none: "p-0",
            sm: "p-3",
            md: "p-6",
            lg: "p-10",
        };

        return (
            <motion.div
                ref={ref}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                    "rounded-2xl transition-all duration-300 overflow-hidden",
                    variants[variant],
                    paddings[padding],
                    className
                )}
                {...props}
            />
        );
    }
);

Card.displayName = "Card";

export default Card;
