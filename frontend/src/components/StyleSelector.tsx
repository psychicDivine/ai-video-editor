interface StyleSelectorProps {
  selectedStyle: string
  onStyleChange: (style: string) => void
}

const styles = [
  {
    id: 'cinematic_drama',
    name: 'Cinematic Drama',
    description: 'Professional, dramatic, moody',
    emoji: '🎭',
  },
  {
    id: 'energetic_dance',
    name: 'Energetic Dance',
    description: 'Fast-paced, confident, dynamic',
    emoji: '💃',
  },
  {
    id: 'luxe_travel',
    name: 'Luxe Travel',
    description: 'Wanderlust, luxury, peaceful',
    emoji: '✈️',
  },
  {
    id: 'modern_minimal',
    name: 'Modern Minimal',
    description: 'Clean, professional, modern',
    emoji: '✨',
  },
]

export default function StyleSelector({ selectedStyle, onStyleChange }: StyleSelectorProps) {
  return (
    <div className="space-y-4">
      {styles.map((style) => (
        <button
          key={style.id}
          onClick={() => onStyleChange(style.id)}
          className={`w-full p-4 rounded-lg border-2 transition text-left ${
            selectedStyle === style.id
              ? 'border-blue-500 bg-blue-900 bg-opacity-30'
              : 'border-slate-600 bg-slate-600 bg-opacity-20 hover:border-slate-500'
          }`}
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">{style.emoji}</span>
            <div>
              <h3 className="font-bold text-white">{style.name}</h3>
              <p className="text-sm text-slate-300">{style.description}</p>
            </div>
          </div>
        </button>
      ))}
    </div>
  )
}
