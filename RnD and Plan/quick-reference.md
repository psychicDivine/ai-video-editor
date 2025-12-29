# Quick Reference: Cinematography Rules for AI Video Generation

**Purpose:** Copy-paste guidelines for your team to understand and implement cinematography in the AI reel generator.

---

## 1. Transition Types & When to Use

```
HARD CUT (0ms)
├─ When: On downbeat / kick drum hit
├─ Energy: HIGH
├─ Feeling: Instant change, shocking, energetic
├─ Used: 60% of professional edits
└─ Prompt hint: "hard cut on beat", "instant transition"

CROSSFADE (200-500ms)
├─ When: Between sections, on sustained notes
├─ Energy: MEDIUM
├─ Feeling: Smooth, emotional, connected
├─ Used: 25% of professional edits
└─ Prompt hint: "smooth fade to", "dissolve into"

ZOOM IN (200-500ms)
├─ When: Focus on detail, emphasize emotion
├─ Energy: BUILDING
├─ Feeling: Closer, more intimate, magnified
├─ Used: 10% of professional edits
└─ Prompt hint: "zoom in on", "close-up transition"

MOTION BLUR (50-150ms)
├─ When: Hide fast cuts, add kinetic energy
├─ Energy: FAST PACED
├─ Feeling: Dynamic, action-packed
├─ Used: 5% (used sparingly)
└─ Prompt hint: "whip pan", "motion blur transition"

REVEAL (300-500ms)
├─ When: Build suspense, cinematic moment
├─ Energy: DRAMATIC
├─ Feeling: Cinematic, professional, intentional
├─ Used: 5% (reserved for dramatic moments)
└─ Prompt hint: "reveal behind", "sliding transition"
```

---

## 2. Beat Synchronization Rules

### Rule 1: Cut On Downbeats
```
Music:    ▓▓▓▓ BEAT ▓▓▓▓ BEAT ▓▓▓▓ BEAT ▓▓▓▓
Timeline: [Shot A   ][Shot B   ][Shot C   ]
                ↑           ↑           ↑
            Cut here    Cut here    Cut here
          (on beat)     (on beat)   (on beat)

Result: Feels professional, intentional
```

### Rule 2: Match Transition Type to Audio Stream

```
DRUM HITS
├─ Visual: Hard cut (0ms)
├─ Timing: Frame-perfect on beat
└─ Energy: Maximum

VOCAL MELODY
├─ Visual: Crossfade or zoom
├─ Timing: Softer, more fluid
└─ Energy: Emotional

BASS DROP
├─ Visual: Brighten/saturate heavily
├─ Timing: Exact beat moment
└─ Energy: Intensity spike
```

### Rule 3: Segment Duration Logic

```
Total Duration: 30 seconds
Number of Segments: 4-6 (based on BPM)

At 120 BPM:
├─ Intro: 3-4 seconds (slow setup)
├─ Build: 4-6 seconds (acceleration)
├─ Peak: 4-6 seconds (climax, most energy)
├─ Resolution: 2-3 seconds (calm down)
└─ Total: 30 seconds

Each segment aligned to beat boundaries
Transitions happen ON beats
```

---

## 3. Lighting Setup (3-Point)

```
          KEY LIGHT (Main)
               ↓
        Angle: 45° above subject
        Distance: 2-3x subject distance
        Strength: BRIGHT (this creates drama)
        Direction: From side creates shadows
        ═══════════════════════════════════
                ┌─────┐
                │  ●  │ ← Subject
                └─────┘
        ▲               ▲
        │               │
       FILL           BACK
     (soft)          (rim)
     │ softens       │ creates
     │ shadows       │ separation
     │ detail        │ from bg
        ═══════════════════════════════════

PROFESSIONAL RESULT:
- Subject well-lit (not too dark)
- Shadows with detail (not black holes)
- Rim light separates subject from background
- No harsh shadows across face
```

---

## 4. Color Temperature & Mood

```
WARM (2700-3200K) → "Golden Hour" Feel
├─ Mood: Energetic, intimate, warm
├─ Use: Dance, celebration, travel
├─ Colors: Golds, oranges, warm reds
├─ Darkness: Rich browns, deep shadows
└─ Example: "Warm golden (2700K) with rich shadows"

COOL (5500-6500K) → "Cinematic" Feel
├─ Mood: Dramatic, professional, moody
├─ Use: Drama, mystery, cinematic
├─ Colors: Blues, teals, cool tones
├─ Darkness: Deep blues, cool blacks
└─ Example: "Cool cinematic (5600K) with blue shadows"

NEUTRAL (4000-4500K) → "Clean" Feel
├─ Mood: Professional, modern, clean
├─ Use: Tech, business, modern
├─ Colors: Balanced, neither warm nor cool
├─ Darkness: Natural blacks
└─ Example: "Neutral daylight (4500K)"

SATURATED → "Vibrant" Feel
├─ Mood: Energetic, stylized, artistic
├─ Use: Neon, vaporwave, retro
├─ Colors: Bright magentas, cyans, neons
└─ Example: "High saturation neon lighting"
```

---

## 5. Composition Rules

### Rule of Thirds
```
Divide frame into 9 sections:

┌─────┬─────┬─────┐
│  1  │  2  │  3  │
├─────┼─────┼─────┤
│  4  │  5  │  6  │  ← Place subject at
├─────┼─────┼─────┤     intersection (dots)
│  7  │  8  │  9  │     NOT in center (5)
└─────┴─────┴─────┘

❌ Wrong: Subject centered
✅ Right: Subject at 1/3 line
Engagement: +66% higher when off-center
```

### Negative Space
```
Subject SMALL, environment LARGE

┌──────────────────────────────┐
│                              │
│         (huge space)         │
│                              │
│         ●                    │  ← Small subject
│    (subject)                 │
│                              │
└──────────────────────────────┘

Use: Establishing shots, epic landscapes, wanderlust
Feeling: Grand, overwhelming, cinematic
```

### Depth Layers
```
FOREGROUND     MID-GROUND      BACKGROUND
(out of focus) (sharp, action) (blurred)

        ↙         ↙              ↙
    ╱╱╱╱╱╱╱  ┌─────────┐  ~~~~~~~
    ╱ blur╱╱  │SUBJECT  │  ~blurry~
    ╱╱╱╱╱╱╱  │ SHARP   │  ~~~~~~~
    ╱╱╱╱╱╱╱  └─────────┘

Result: Professional depth, 3D feel
```

---

## 6. Camera Movement Style Guide

```
STATIC (No Movement)
├─ Feeling: Controlled, thoughtful
├─ Use: Dialogue, emotional moment
└─ BPM: Any

SLOW PAN (Horizontal 2-5 seconds)
├─ Feeling: Cinematic, discovery, wanderlust
├─ Use: Landscape, travel, exploration
└─ BPM: Slow (80-110 BPM)

ZOOM IN/OUT (Slow 2-4 seconds)
├─ Feeling: Emphasis, emotional intensity
├─ Use: Building tension, focus
└─ BPM: Slow to medium (80-130 BPM)

TRACKING SHOT (Smooth following)
├─ Feeling: Dynamic but controlled
├─ Use: Action, movement, following subject
└─ BPM: Medium to fast (100-140 BPM)

WHIP PAN (Fast horizontal move)
├─ Feeling: Energetic, action-packed
├─ Use: Transitions, fast-paced content
└─ BPM: Fast (130+ BPM)

DOLLYING (Forward/backward movement)
├─ Feeling: Most cinematic, professional
├─ Use: Approach subjects, depth building
└─ BPM: Slow to medium (70-120 BPM)
```

---

## 7. Color Consistency Checklist

Before rendering, verify:

```
□ All clips have similar average brightness (±10 units)
□ Skin tones are warm (not blue/green cast)
□ Shadows have detail (not pure black #000000)
□ Highlights not blown out (not pure white #FFFFFF)
□ Saturation consistent across cuts
□ Color temperature same throughout (warm/cool/neutral)
□ No flickering between clips
□ Color grading enhances mood without looking "filtered"

Brightness Range: 100-150 out of 255 (moderate brightness)
Saturation: 60-80 out of 100 (natural, not oversaturated)
Contrast: 1.2-1.5x ratio (punchy, not flat)
```

---

## 8. Prompt Template (Copy-Paste)

### For Dance/Energetic Content:
```
Professional cinematic dance video.
Duration: {X} seconds exactly.
Resolution: 1080x1920 (vertical 9:16).

Camera: {CAMERA_MOVEMENT}
Composition: {COMPOSITION_RULE}
Lighting: {LIGHTING_SETUP}
Color: {COLOR_PALETTE}

{USER_CREATIVE_DIRECTION}

Ensure:
- Consistent warm golden tones (2700K)
- Professional 3-point lighting
- No harsh shadows
- Bright key light in every shot
- Subject positioned at rule of thirds intersection
```

### For Cinematic/Dramatic Content:
```
Professional cinematic video with dramatic storytelling.
Duration: {X} seconds exactly.
Resolution: 1080x1920 (vertical 9:16).

Camera: Slow, deliberate movements with precision
Composition: Symmetrical, layered depth
Lighting: Dramatic 3-point lighting with strong key light
Color: Cool cinematic (5500K), rich shadows, desaturated

{USER_CREATIVE_DIRECTION}

Ensure:
- Every shot intentional and composed
- High contrast for drama
- Cool color temperature throughout
- Professional color grading
- Deep shadows with detail (not pure black)
```

### For Travel/Luxe Content:
```
Professional cinematic travel video with wanderlust appeal.
Duration: {X} seconds exactly.
Resolution: 1080x1920 (vertical 9:16).

Camera: Slow tracking shots, gentle parallax effect
Composition: Leading lines, negative space, rule of thirds
Lighting: Golden hour backlighting, rim light, soft shadows
Color: Warm golden (3200K), saturated oranges/yellows

{USER_CREATIVE_DIRECTION}

Ensure:
- Golden hour cinematography throughout
- Backlit subjects for separation
- No harsh shadows
- Warm, inviting color grading
- Layered depth with foreground/background
```

---

## 9. Quality Gates (FFmpeg Checks)

Run before delivery:

```bash
# Check 1: Duration (should be ~30 seconds)
ffprobe -show_entries format=duration {video.mp4}
Result: 25-35 seconds ✓

# Check 2: Resolution (must be 1080x1920)
ffprobe -show_entries stream=width,height {video.mp4}
Result: width=1080, height=1920 ✓

# Check 3: Codec (must be H.264)
ffprobe -show_entries stream=codec_name {video.mp4}
Result: codec_name=h264 ✓

# Check 4: Audio (must have AAC audio)
ffprobe -select_streams a:0 {video.mp4}
Result: codec_name=aac ✓

# Check 5: Frame rate (24 or 30fps)
ffprobe -show_entries stream=r_frame_rate {video.mp4}
Result: r_frame_rate=24/1 or 30/1 ✓

# Check 6: Bitrate (300-500 kbps video)
ffprobe -show_entries stream=bit_rate {video.mp4}
Result: 350000-500000 bits ✓
```

---

## 10. Common Mistakes to Avoid

```
❌ MISTAKE #1: Random color shifts between clips
   FIX: Analyze first clip, match all others to it

❌ MISTAKE #2: Cutting at random times
   FIX: Always cut ON beat boundaries (within ±2 frames)

❌ MISTAKE #3: Harsh, unlit subjects
   FIX: Use 3-point lighting in every prompt

❌ MISTAKE #4: Inconsistent transitions
   FIX: Hard cuts on drums, fades on sustained notes

❌ MISTAKE #5: No composition guidance in prompts
   FIX: Always specify rule of thirds, depth layers

❌ MISTAKE #6: Audio doesn't match visuals
   FIX: Sync cuts to beat times from beat detector

❌ MISTAKE #7: Over-saturated or flat colors
   FIX: Maintain saturation 60-80 range

❌ MISTAKE #8: Unexpected color casts (blue/green)
   FIX: Specify warm/cool tone in every prompt

❌ MISTAKE #9: Flickering between clips
   FIX: Test color match before rendering

❌ MISTAKE #10: Looks "AI-generated"
   FIX: Use all layers: prompt engineering + color matching + LUT
```

---

## 11. Style Presets at a Glance

| Style | Camera | Lighting | Color | Transitions | Mood |
|-------|--------|----------|-------|------------|------|
| **Cinematic Drama** | Slow, deliberate | Dramatic key light, high contrast | Cool (5600K), desaturated | Dissolves (500ms) | Professional, serious |
| **Energetic Dance** | Dynamic pans/zooms | Bright key, minimal fill | Warm (2700K), saturated | Hard cuts (0ms) | Confident, energetic |
| **Luxe Travel** | Slow tracking | Golden hour backlighting | Warm (3200K), saturated | Slow dissolves (500ms+) | Wanderlust, luxury |
| **Vaporwave Neon** | Stylized, zoom on objects | Neon/synthetic lighting | Cool neons (blues, magentas) | Sharp cuts | Retro-futuristic, artistic |
| **Film Noir** | Static or slow pans | High contrast, strong shadows | Desaturated, cool | Hard cuts, fade to black | Mysterious, timeless |
| **Modern Minimal** | Static or subtle | Soft, even lighting | Neutral (4500K), low sat | Subtle fades | Clean, modern, sophisticated |

---

## 12. Implementation Checklist

For your development team:

```
BACKEND IMPLEMENTATION:
□ Enum classes for StylePreset and ColorPalette
□ Gemini integration for segment planning
□ Beat analysis algorithm
□ Color analysis (OpenCV)
□ Color matching (FFmpeg curves)
□ LUT application (FFmpeg)
□ Concat with transitions (FFmpeg)
□ Quality gates (ffprobe checks)
□ Integration into worker pipeline

TESTING:
□ Test each style preset with sample prompts
□ Verify beat detection accuracy
□ Test color matching on diverse generated clips
□ Verify LUT application improves consistency
□ End-to-end test: prompt → final video
□ A/B test with users (AI vs manual)

DOCUMENTATION:
□ Add style presets to API docs
□ Document color palette options
□ Create user guide for cinematography tips
□ Share these quick references with team
```

---

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Production-Ready Quick Reference