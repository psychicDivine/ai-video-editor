import { Zap, Sparkles, Flame, Film, Plane, Check } from 'lucide-react';
import { cn } from '../ui/utils';

interface StyleSelectorProps {
  selectedStyle: string
  onStyleChange: (style: string) => void
}

// Style definitions synced with backend style_editor.py
// These IDs must match exactly with backend STYLE_CONFIGS keys
const styles = [
  {
    id: 'cinematic_drama',
    name: 'Cinematic',
    shortDesc: 'Dramatic & Moody',
    prompt: 'Slow 4-6s cuts, crossfades, cool tones',
    icon: Film,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    activeBg: 'bg-purple-500/20'
  },
  {
    id: 'energetic_dance',
    name: 'Energetic',
    shortDesc: 'Fast & Bold',
    prompt: 'Beat-synced cuts, speed ramps, zoom punch',
    icon: Zap,
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    activeBg: 'bg-orange-500/20'
  },
  {
    id: 'luxe_travel',
    name: 'Travel',
    shortDesc: 'Smooth & Golden',
    prompt: 'Ken Burns zoom, warm tones, elegant flow',
    icon: Plane,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    activeBg: 'bg-amber-500/20'
  },
  {
    id: 'modern_minimal',
    name: 'Minimal',
    shortDesc: 'Clean & Pro',
    prompt: 'Clean cuts, neutral colors, steady pace',
    icon: Sparkles,
    color: 'text-slate-300',
    bg: 'bg-white/5',
    border: 'border-white/20',
    activeBg: 'bg-white/10'
  },
  {
    id: 'viral_tiktok',
    name: 'Viral',
    shortDesc: 'Hook & Energy',
    prompt: 'Fast cuts, freeze frames, high saturation',
    icon: Flame,
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
    border: 'border-pink-500/30',
    activeBg: 'bg-pink-500/20'
  },
]

export default function StyleSelector({ selectedStyle, onStyleChange }: StyleSelectorProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between px-1">
        <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted">AI Style</span>
        <Sparkles size={12} className="text-reel/50" />
      </div>
      
      <div className="flex flex-col gap-1.5">
        {styles.map((style) => {
          const isSelected = selectedStyle === style.id;
          return (
            <button
              type="button"
              key={style.id}
              onClick={() => onStyleChange(style.id)}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg border transition-all duration-200",
                isSelected
                  ? `${style.activeBg} ${style.border} shadow-sm`
                  : "border-transparent bg-white/5 hover:bg-white/10"
              )}
            >
              {/* Icon */}
              <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                style.bg
              )}>
                <style.icon size={16} className={style.color} />
              </div>
              
              {/* Text */}
              <div className="flex-1 text-left min-w-0">
                <div className="text-xs font-semibold text-text-primary truncate">{style.name}</div>
                <div className="text-[9px] text-text-muted truncate">{style.prompt}</div>
              </div>
              
              {/* Selection Indicator */}
              {isSelected && (
                <div className={cn("w-5 h-5 rounded-full flex items-center justify-center shrink-0", style.bg)}>
                  <Check size={12} className={style.color} />
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  )
}
