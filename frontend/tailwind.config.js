/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Futuristic Palette
        background: '#0b0f14', // Deep space black
        panel: '#161b22',      // Card background
        surface: '#1c2128',    // Input background
        neon: {
          green: '#39FF7A',    // Primary Action / Beat
          blue: '#00F0FF',     // Secondary / Info
          purple: '#B026FF',   // Accent
          pink: '#FF2A6D',     // Highlight
        },
        amber: {
          400: '#FFD166',      // Warning / Attention
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'], // Tech feel
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'neon-green': '0 0 10px rgba(57, 255, 122, 0.5)',
        'neon-blue': '0 0 10px rgba(0, 240, 255, 0.5)',
      }
    },
  },
  plugins: [],
}
