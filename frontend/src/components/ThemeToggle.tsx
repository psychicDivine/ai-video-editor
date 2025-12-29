import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try {
      const stored = localStorage.getItem('theme')
      return (stored as 'dark' | 'light') || 'dark'
    } catch (e) {
      return 'dark'
    }
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    try {
      localStorage.setItem('theme', theme)
    } catch (e) {
      /* ignore */
    }
  }, [theme])

  return (
    <button
      aria-label="Toggle theme"
      onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
      className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-slate-700 hover:bg-slate-600 text-slate-100"
    >
      {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      <span className="text-sm">{theme === 'dark' ? 'Light' : 'Dark'}</span>
    </button>
  )
}
