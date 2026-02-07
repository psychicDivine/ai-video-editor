/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--bg-canvas)',
        surface: 'var(--bg-surface)',
        'surface-elevated': 'var(--bg-surface-elevated)',
        primary: {
          DEFAULT: 'var(--primary)',
          muted: 'var(--primary-muted)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        border: 'var(--border)',
        reel: {
          DEFAULT: 'var(--reel)',
          glow: 'var(--reel-glow)',
        },
        podcast: {
          DEFAULT: 'var(--podcast)',
          glow: 'var(--podcast-glow)',
        },
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        accent: 'var(--accent)',
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        display: ['"Outfit"', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.8)',
        'neon-reel': '0 0 20px rgba(0, 240, 255, 0.3)',
        'neon-podcast': '0 0 20px rgba(176, 38, 255, 0.3)',
        'neon-primary': '0 0 20px rgba(59, 130, 246, 0.3)',
      }
    },
  },
  plugins: [],
}
