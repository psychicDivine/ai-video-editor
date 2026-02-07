
import { useState, useEffect } from "react";
import axios from "axios";

interface CaptionStyle {
    name: string;
    description: string;
    preview_color: string;
}

interface CaptionStyleSelectorProps {
    selectedStyle: string;
    onStyleChange: (style: string) => void;
}

export default function CaptionStyleSelector({ selectedStyle, onStyleChange }: CaptionStyleSelectorProps) {
    const [styles, setStyles] = useState<Record<string, CaptionStyle>>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch available styles from backend
        axios.get("http://localhost:8000/api/captions/styles")
            .then(res => {
                setStyles(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load caption styles", err);
                // Fallback defaults
                setStyles({
                    "classic": { name: "Classic", description: "Clean white text", preview_color: "#FFFFFF" },
                    "tiktok": { name: "TikTok", description: "Viral yellow highlight", preview_color: "#FFFF00" },
                    "hormozi": { name: "Hormozi", description: "Impact font top", preview_color: "#00FF00" },
                    "neon": { name: "Neon", description: "Glowing colors", preview_color: "#FF00FF" }
                });
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="text-xs text-slate-500">Loading styles...</div>;

    return (
        <div className="grid grid-cols-2 gap-3 mt-2">
            {Object.entries(styles).map(([key, style]) => (
                <button
                    key={key}
                    type="button"
                    onClick={() => onStyleChange(key)}
                    className={`
            relative p-3 rounded-xl border-2 text-left transition-all group overflow-hidden
            ${selectedStyle === key
                            ? "border-blue-500 bg-blue-500/10"
                            : "border-slate-800 bg-slate-900/50 hover:border-slate-700"}
          `}
                >
                    {/* Color Preview Dot */}
                    <div
                        className="absolute top-3 right-3 w-3 h-3 rounded-full shadow-lg"
                        style={{
                            backgroundColor: style.preview_color.replace("&H00", "#").replace("&H", "#")
                            // ASS format &H00BBGGRR conversion in JS is tricky without parsing, 
                            // but assuming standard hex fallback for dot color
                        }}
                    />

                    <div className="font-bold text-sm text-slate-200 group-hover:text-white">
                        {style.name}
                    </div>
                    <div className="text-[10px] text-slate-400 leading-tight mt-1">
                        {style.description}
                    </div>
                </button>
            ))}
        </div>
    );
}
