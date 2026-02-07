# Theme System

## Available Themes

Studio AI now supports 5 beautiful themes:

### 🌑 **Dark** (Default)
Professional dark theme with blue accents. Perfect for extended editing sessions.

### ☀️ **Light**
Clean, high-contrast light theme with excellent readability. Ideal for well-lit environments.

### 🌃 **Midnight**
Pure black OLED theme with cool blue tones. Battery-friendly for OLED displays.

### 🏔️ **Nord**
Arctic-inspired palette with muted pastels. Easy on the eyes with Scandinavian aesthetics.

### 🌅 **Sunset**
Warm evening vibes with pink and orange gradients. Creative and energetic atmosphere.

## How to Change Theme

1. Click your **profile avatar** in the top-right corner
2. Select **"Appearance"** from the menu
3. Choose your preferred theme
4. Theme preference is saved automatically

## Customization

Themes are defined in `/frontend/src/index.css` using CSS custom properties.

Each theme defines:
- Background colors (canvas, surface, elevated)
- Text colors (primary, secondary, muted)
- Brand colors (reel, podcast)
- UI colors (primary, accent, success, warning, danger)
- Border and shadow tokens

## For Developers

Theme switching uses `data-theme` attribute on the root element:

```tsx
import { useApp } from './context/AppContext';

function MyComponent() {
  const { theme, setTheme } = useApp();
  
  return (
    <button onClick={() => setTheme('nord')}>
      Switch to Nord
    </button>
  );
}
```

Themes persist in `localStorage` under the key `app-theme`.
