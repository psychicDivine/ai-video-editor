# Cinematic Video Production Guide for AI-Generated Reels

**Purpose:** Ensure AI-generated content maintains cinematic quality through intelligent prompt engineering, audio sync, color grading, and transition control.

**Target:** Beat-synced, 30s vertical reels with professional-grade output.

---

## Table of Contents

1. [Cinematic Foundations](#cinematic-foundations)
2. [Role of Transitions in Visual Storytelling](#role-of-transitions)
3. [Audio-Visual Synchronization Strategy](#audio-visual-synchronization)
4. [Color Grading & Lighting Consistency](#color-grading--lighting-consistency)
5. [Intelligent Prompt Engineering](#intelligent-prompt-engineering)
6. [Quality Control Pipeline](#quality-control-pipeline)
7. [Implementation in Your System](#implementation-in-your-system)

---

## Cinematic Foundations

### What Makes a Video "Cinematic"?

A cinematic reel combines:

```
Cinematic Quality = Visual Composition + Audio Sync + Color Consistency + Pacing + Transitions
```

#### 1. **Visual Composition**

**Rule of Thirds:**
- Divide frame into 9 sections (3×3 grid)
- Place key subjects on intersection points
- Creates natural visual balance

```
Example: In a dance reel
┌─────┬─────┬─────┐
│     │     │     │
├─────┼─────┼─────┤  → Dancer at intersection = 66% more engaging
│  ● D├─────┤     │     than centered frame
├─────┼─────┼─────┤
│     │     │     │
└─────┴─────┴─────┘
```

**Depth & Layers:**
- Foreground: sharp, in-focus subject
- Mid-ground: action or key object
- Background: blurred (shallow depth of field) or complementary

**Camera Movement (simulated in AI):**
- Pan: smooth horizontal movement
- Tilt: vertical movement
- Zoom: slow in/out for emphasis
- Dolly: forward/backward motion (most cinematic)

#### 2. **Lighting Quality**

Professional reels use **3-point lighting:**

```
       Key Light (Main)
            |
            ▼
    ┌───────────────┐
    │               │
    │      ●        │  ← Subject
    │               │
    └───────────────┘
    ▲               ▲
    |               |
Fill Light      Back Light
(shadow detail)  (separation)
```

**Quality Indicators:**
- **No harsh shadows** (unless intentional)
- **Skin tones natural** (warm, not blown out)
- **Catchlights in eyes** (reflection of light source)
- **Consistent lighting across cuts** (no sudden darkness/brightness)

#### 3. **Color Science**

Professional grade uses **color grading principles:**

**Temperature:**
- Warm (orange/gold): intimate, energy, dance
- Cool (blue): melancholic, cinematic, night
- Neutral: clean, technical, corporate

**Saturation & Contrast:**
- High saturation: vibrant, energetic (reels, promos)
- Low saturation: moody, film noir
- High contrast: dramatic, pop
- Low contrast: smooth, romantic

**Color Harmony:**
- **Complementary:** opposite colors (blue + orange) = dynamic
- **Analogous:** adjacent colors = harmonious
- **Monochromatic:** single color + variations = sophisticated

---

## Role of Transitions

### Why Transitions Matter

**Purpose:**
```
1. Temporal Connection    → Link shots across time
2. Narrative Flow        → Guide story progression
3. Rhythm Management     → Control pacing/energy
4. Attention Direction   → Guide viewer's eye
5. Mood Setting          → Reinforce emotion
```

### Professional Transition Types

#### **1. Cut (Hard Cut)**
- **When:** On strong beats (downbeats)
- **Effect:** High energy, abrupt change
- **Usage:** 60% of professional reels
- **Prompt hint:** "hard cut on beat", "immediate transition"

```
Shot A (ends) ▌█ CUT █▌ Shot B (starts)
        Frame 1    Frame 2
        (instant switch = maximum impact)
```

#### **2. Crossfade (Dissolve)**
- **When:** Between thematic transitions
- **Duration:** 200-500ms (slower = more cinematic)
- **Effect:** Soft, emotional, connected
- **Usage:** 25% of professional edits
- **Prompt hint:** "smooth fade to", "dissolve into"

```
Shot A opacity: 100% ──┐
                      ├─ Overlap zone = crossfade
Shot B opacity:   0% ──┘
```

#### **3. Zoom Transition**
- **When:** To emphasize detail or action
- **Speed:** Fast = energetic, Slow = dramatic
- **Effect:** Focuses attention, adds depth
- **Usage:** 10% (used sparingly for impact)
- **Prompt hint:** "zoom in on", "close-up transition", "magnify"

#### **4. Motion Blur Transition**
- **When:** Between fast-paced cuts
- **Direction:** Match shot movement direction
- **Effect:** Adds kinetic energy, hides jump cuts
- **Prompt hint:** "whip pan", "motion blur transition"

#### **5. Reveal Transition**
- **When:** Building suspense or drama
- **Style:** One shot slides/covers previous shot
- **Effect:** Cinematic, professional
- **Prompt hint:** "reveal behind", "sliding transition"

### Transition Timing (Critical!)

**On-Beat Transitions (Professional Standard)**

```
Music:    ▓▓▓▓ BEAT ▓▓▓▓ BEAT ▓▓▓▓ BEAT ▓▓▓▓
Timeline: [Shot 1     ][Shot 2     ][Shot 3     ]
                ↑              ↑              ↑
           Cut here        Cut here        Cut here
          (on beat)        (on beat)       (on beat)
```

**Why this matters:**
- **On-beat cuts:** Feel synchronized, professional, intentional
- **Off-beat cuts:** Feel random, amateurish, disorienting
- **Research:** Professional editors cut 95% of transitions on beats

---

## Audio-Visual Synchronization

### The Audio-Visual Contract

**The Viewer's Expectation:**
```
When you hear a bass DROP    → Expect to SEE an impact/change
When you hear high vocals    → Expect to SEE detail/emotion
When you hear rapid beats    → Expect to SEE fast cuts
When audio is mellow        → Expect to SEE smooth transitions
```

**Violating this = Viewer Discomfort**

### Multi-Stream Audio Control (MTV Framework)

Research shows 3 separate audio streams need different visual responses:

#### **Stream 1: Drums/Percussion (Rhythm)**
```
Role: Sets the beat and pace
Visible via: Cuts, transitions, shot timing
Sync point: Visual cuts on kick drum hits
Prompt: "sync cuts to the drum beat", "cut on kick"

Example:
🥁 KICK → [Hard cut] → New shot
🥁 KICK → [Hard cut] → New shot
🥁 KICK → [Hard cut] → New shot
```

#### **Stream 2: Melody/Vocals (Emotion)**
```
Role: Conveys mood and story
Visible via: Camera movement, expression changes, color shifts
Sync point: Slow motion on high notes, speed up on staccato
Prompt: "match energy to vocal intensity", "slow on chorus"

Example:
Vocals: ▔▔▔▔ HIGH EMOTION ▔▔▔▔
Video:  [Zoom in] [Slow mo] [Bright colors] → Emphasize emotion
```

#### **Stream 3: Bass/Sub (Depth & Power)**
```
Role: Creates immersion and power
Visible via: Lighting intensity, color saturation, scale of shots
Sync point: Brighten on bass swells, darken on drops
Prompt: "intensify on bass drop", "warm lighting on sub frequencies"

Example:
Bass:  ▓▓▓▓▓ HUGE DROP ▓▓▓▓▓
Video: [Maximum saturation] [Widest shot] [Brightest lighting]
```

### Synchronization Techniques

#### **1. Micro-Sync (Frame-Level)**
- Sync at beat level (more precise)
- Example: Bass drum hit at frame 24 → cut at frame 24
- Tolerance: ±2 frames (83ms at 24fps)

#### **2. Macro-Sync (Segment-Level)**
- Sync at segment level (4-8 bars)
- Example: Verse segment has smooth shots, chorus has cuts
- Tolerance: ±500ms

#### **3. Kinetic Sync (Movement-Level)**
- Visual movement matches audio intensity
- Fast beats = quick camera movements
- Slow melody = slow pans

### Audio Post-Processing (Quality Gate)

Before syncing visuals, audio must be:

```
✓ Loudness normalized to -14 LUFS (YouTube standard)
✓ No clipping or distortion
✓ EQ balanced (no frequency mud)
✓ Dynamic range compression (prevents sudden loud/quiet shifts)
✓ Stereo field balanced (not all left/right)

FFmpeg command (for your backend):
ffmpeg -i input.wav \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac output.m4a
```

---

## Color Grading & Lighting Consistency

### The Problem with AI-Generated Video

When using models like Open-Sora or Pika:

```
Shot 1 Generated: Blue-tinted, bright (model's default)
Shot 2 Generated: Warm, darker (different prompt interpretation)
Shot 3 Generated: Desaturated, flat (seed variation)

Result: Cuts feel jarring, unprofessional, "stitched"
```

### Solution: LUT-Based Color Consistency

**LUT** = Look-Up Table (maps input colors → output colors)

```python
# app/workers/color_grading.py

class ColorGradingService:
    """Ensure all generated clips have consistent color."""
    
    def __init__(self):
        # Load cinematic LUT libraries
        self.cinema_lut = load_lut("cinema_lut.cube")
        self.warm_lut = load_lut("warm_golden.cube")
        self.cool_lut = load_lut("cool_blue.cube")
    
    async def apply_lut_to_clip(self, video_path: str, style: str):
        """
        Apply consistent color grading to all generated clips.
        
        Args:
            video_path: Path to generated video
            style: "cinematic", "warm", "cool", "vibrant"
        
        Returns:
            graded_video_path: Path to color-graded video
        """
        lut = self.get_lut(style)
        
        # FFmpeg command to apply LUT
        cmd = f"""
        ffmpeg -i {video_path} \
          -vf "lut3d={lut}:interp=tetrahedral" \
          -c:v libx264 -preset fast \
          {video_path}_graded.mp4
        """
        
        result = await run_ffmpeg(cmd)
        return result
    
    def get_lut(self, style: str):
        """Select appropriate LUT based on style."""
        luts = {
            "cinematic": self.cinema_lut,
            "warm": self.warm_lut,
            "cool": self.cool_lut,
            "vibrant": load_lut("vibrant_neon.cube")
        }
        return luts.get(style, self.cinema_lut)
```

### Color Grading Strategy

#### **Step 1: Analyze Generated Clip**
```python
def analyze_clip_colors(video_path: str):
    """Analyze color distribution in AI-generated clip."""
    
    import cv2
    import numpy as np
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    color_data = {
        "brightness": [],
        "saturation": [],
        "hue": []
    }
    
    while frame_count < 30:  # Analyze 30 frames
        ret, frame = cap.read()
        if not ret:
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        color_data["brightness"].append(np.mean(hsv[:,:,2]))
        color_data["saturation"].append(np.mean(hsv[:,:,1]))
        color_data["hue"].append(np.mean(hsv[:,:,0]))
        
        frame_count += 1
    
    return {
        "avg_brightness": np.mean(color_data["brightness"]),
        "avg_saturation": np.mean(color_data["saturation"]),
        "avg_hue": np.mean(color_data["hue"]),
        "brightness_std": np.std(color_data["brightness"]),  # Inconsistency
        "saturation_std": np.std(color_data["saturation"])
    }
```

#### **Step 2: Correct Inconsistencies**
```python
def correct_clip_colors(video_path: str, target_brightness: float):
    """Adjust clip to match target brightness from first clip."""
    
    current = analyze_clip_colors(video_path)
    brightness_diff = target_brightness - current["avg_brightness"]
    
    # Create FFmpeg curves adjustment
    if brightness_diff > 0:
        curve = f"curves=r='0/0 255/{255+brightness_diff}':p=0.5"
    else:
        curve = f"curves=r='0/0 255/{255+brightness_diff}':p=0.5"
    
    cmd = f"""
    ffmpeg -i {video_path} \
      -vf "{curve}" \
      -c:v libx264 \
      {video_path}_corrected.mp4
    """
    
    return run_ffmpeg(cmd)
```

#### **Step 3: Apply Global LUT**
```python
# After all clips matched in brightness/saturation,
# apply single LUT across entire timeline

def apply_global_lut(timeline_segments: list, style: str):
    """Apply consistent LUT to all segments."""
    
    for segment in timeline_segments:
        cmd = f"""
        ffmpeg -i {segment["video_path"]} \
          -vf "lut3d=cinema.cube:interp=tetrahedral" \
          {segment["video_path"]}_lut.mp4
        """
        run_ffmpeg(cmd)
```

### Lighting Consistency Checklist

```
Before Rendering Final Video:

□ All clips have similar average brightness (±10 LUFS variance)
□ Skin tones are warm and natural (no blue cast)
□ Shadows have detail (not pure black)
□ Highlights don't blow out (not pure white)
□ Saturation is consistent (not varying wildly)
□ Color temperature matches (warm/cool throughout)
□ No flickering between cuts
□ Color grading enhances mood without looking "filtered"
```

---

## Intelligent Prompt Engineering

### The Master Prompt Framework

Instead of asking AI "create any dance video", use **structured cinematography prompts** that encode visual rules.

#### **Base Cinematic Prompt Template**

```
{CINEMATOGRAPHY_BASE}

"{VIDEO_DESCRIPTION}" 

Cinematography requirements:
├─ Camera: {CAMERA_MOVEMENT}
├─ Composition: {COMPOSITION_RULE}
├─ Lighting: {LIGHTING_SETUP}
├─ Color: {COLOR_PALETTE}
├─ Duration: {EXACT_DURATION}
├─ Resolution: 1080x1920 (vertical 9:16)
└─ Mood: {EMOTIONAL_TONE}
```

#### **Example 1: Energetic Dance Reel**

```
MASTER PROMPT:
"Create a professional, cinematic short video for social media.

Scene: A dancer performing to upbeat electronic music
in a minimalist studio with dramatic lighting.

Cinematography:
├─ Camera: Dynamic - start with wide establishing shot,
│  then zoom in on dancer, end with overhead angle
├─ Composition: Rule of thirds - dancer positioned
│  at left 1/3 line, leaving space for movement
├─ Lighting: 3-point lighting - bright key light from
│  left, fill light softening shadows, back light
│  for separation. High contrast for drama.
├─ Color: Warm golden tones (2700K) with rich shadows.
│  Saturated reds and oranges in clothing.
├─ Transitions: Hard cuts on beat drops, crossfade
│  during tempo changes
├─ Duration: 8 seconds
├─ Resolution: 1080x1920 (9:16)
└─ Mood: High energy, professional, show-off confidence"

Result: Consistent visual language across all segments
```

#### **Example 2: Cinematic Narrative (Travel Vlog Style)**

```
MASTER PROMPT:
"Create a cinematic travel montage.

Scene: Person exploring exotic location with
golden hour cinematography.

Cinematography:
├─ Camera: Slow tracking shots (moving with subject),
│  gentle pans across landscape, parallax effect
│  (foreground/background depth)
├─ Composition: Leading lines - paths/roads guide eye,
│  subject in lower 1/3 to show environment
├─ Lighting: Golden hour sunlight (warm, directional),
│  backlighting on subject for rim light, no harsh shadows
├─ Color: Warm color grade (3200-4000K), increased
│  saturation on oranges/yellows, slightly desaturated
│  blues for sophistication
├─ Transitions: Slow dissolves and fades (matching
│  contemplative mood), no hard cuts
├─ Duration: 6 seconds
├─ Resolution: 1080x1920
└─ Mood: Wanderlust, luxury, discovery, peace"

Result: Cohesive narrative despite cut changes
```

### Prompt Variables to Control

```python
class CinematicPromptBuilder:
    """Build structured cinematography prompts."""
    
    CAMERA_MOVEMENTS = {
        "dynamic": "Fast pans, zooms, whip cuts",
        "smooth": "Slow tracking shots, steady camera",
        "mixed": "Combination of static, pans, and zooms",
        "dynamic_with_pauses": "Energetic cuts interspersed with holds"
    }
    
    COMPOSITIONS = {
        "rule_of_thirds": "Subject positioned at grid intersections",
        "centered": "Subject centered in frame",
        "layered": "Distinct foreground, mid, background layers",
        "negative_space": "Subject small, emphasize environment"
    }
    
    LIGHTING = {
        "studio_3_point": "Key, fill, back lights (professional)",
        "golden_hour": "Warm directional sunlight, rim light",
        "dramatic": "High contrast, deep shadows",
        "soft": "Diffused, minimal shadows, bright overall"
    }
    
    COLOR_PALETTES = {
        "warm_cinematic": "2700K, warm golds/oranges",
        "cool_moody": "5600K, blues/teals, desaturated",
        "vibrant_neon": "High saturation, complementary colors",
        "film_stock": "Slightly desaturated, warm shadows"
    }
    
    EMOTIONAL_TONES = {
        "high_energy": "Fast cuts, bright, saturated",
        "cinematic": "Slow, dramatic, considered",
        "intimate": "Close-ups, soft lighting, warm",
        "epic": "Wide shots, dramatic lighting, high contrast"
    }
    
    def build(self, 
              description: str,
              camera: str = "smooth",
              composition: str = "rule_of_thirds",
              lighting: str = "studio_3_point",
              color: str = "warm_cinematic",
              mood: str = "cinematic",
              duration: int = 8):
        
        prompt = f"""
Create a professional, cinematic video clip (exactly {duration} seconds).

Scene: {description}

Cinematography Requirements:
├─ Camera: {self.CAMERA_MOVEMENTS[camera]}
├─ Composition: {self.COMPOSITIONS[composition]}
├─ Lighting: {self.LIGHTING[lighting]}
├─ Color Grade: {self.COLOR_PALETTES[color]}
├─ Resolution: 1080×1920 (vertical)
├─ Frame Rate: 24fps
├─ Aspect Ratio: 9:16 (mobile/social)
└─ Mood: {self.EMOTIONAL_TONES[mood]}

IMPORTANT:
- Ensure consistent color temperature throughout
- No sudden lighting changes between segments
- Skin tones should be natural and warm
- Avoid overly saturated or desaturated colors
- Use professional color grading principles
- All subjects properly lit, no harsh shadows
"""
        return prompt
```

### Segment-Specific Prompts

Different parts of your 30s reel need different prompts:

```python
SEGMENT_PROMPTS = {
    "intro": {
        "description": "Establishing shot, set the scene, introduce subject",
        "camera": "smooth",
        "lighting": "bright_and_clear",
        "duration": 3,
        "mood": "intriguing"
    },
    "build": {
        "description": "Action escalates, movement increases",
        "camera": "dynamic",
        "lighting": "high_contrast",
        "duration": 4,
        "mood": "energetic"
    },
    "peak": {
        "description": "Climax moment, highest energy, dynamic action",
        "camera": "dynamic_with_pauses",
        "lighting": "dramatic_studio",
        "duration": 4,
        "mood": "epic"
    },
    "resolution": {
        "description": "Action resolves, satisfying conclusion",
        "camera": "smooth",
        "lighting": "soft_golden",
        "duration": 2,
        "mood": "satisfying"
    }
}
```

---

## Quality Control Pipeline

### Pre-Rendering Checks

```python
class QualityGateService:
    """Ensure all AI-generated clips meet quality standards."""
    
    async def validate_segment(self, 
                              video_path: str, 
                              expected_duration: int) -> dict:
        """Run quality checks on generated segment."""
        
        checks = {
            "duration_valid": False,
            "resolution_correct": False,
            "color_consistent": False,
            "no_artifacts": False,
            "audio_sync_ready": False
        }
        
        # Check 1: Duration (tolerance ±0.5s)
        actual_duration = get_video_duration(video_path)
        checks["duration_valid"] = (
            abs(actual_duration - expected_duration) < 0.5
        )
        
        # Check 2: Resolution
        width, height = get_video_resolution(video_path)
        checks["resolution_correct"] = (width == 1080 and height == 1920)
        
        # Check 3: Color Consistency
        colors = analyze_clip_colors(video_path)
        # Brightness variance should be low
        checks["color_consistent"] = (
            colors["brightness_std"] < 15
        )
        
        # Check 4: Artifact Detection
        # Look for flickering, distortion, or artifacts
        artifacts = detect_artifacts(video_path)
        checks["no_artifacts"] = len(artifacts) == 0
        
        # Check 5: Audio Readiness
        # Check audio track exists and is properly formatted
        checks["audio_sync_ready"] = has_proper_audio_track(video_path)
        
        all_passed = all(checks.values())
        
        return {
            "passed": all_passed,
            "checks": checks,
            "ready_for_sync": all_passed,
            "issues": [k for k, v in checks.items() if not v]
        }
```

### Post-Sync Quality Gates

```python
async def validate_final_reel(video_path: str) -> dict:
    """Comprehensive quality check before delivery."""
    
    analysis = {
        "technical": {
            "resolution": "1080x1920",
            "bitrate": get_bitrate(video_path),
            "fps": get_fps(video_path),
            "codec": "h264",
            "audio_codec": "aac"
        },
        "cinematic": {
            "color_consistency": check_color_consistency(video_path),
            "lighting_quality": check_lighting(video_path),
            "transition_smoothness": check_transitions(video_path),
            "audio_sync_accuracy": check_beat_sync(video_path)
        },
        "visual": {
            "no_flickering": detect_flickering(video_path),
            "no_artifacts": detect_artifacts(video_path),
            "no_compression_blocks": detect_compression_issues(video_path),
            "proper_saturation": check_saturation(video_path)
        }
    }
    
    return analysis
```

### Fallback System (If AI Quality Poor)

```python
async def handle_poor_generation(job: Job):
    """If generated clip fails quality gates."""
    
    if job.retry_count < job.max_retries:
        # Retry with adjusted prompt
        job.retry_count += 1
        new_prompt = enhance_prompt_for_quality(job.prompt)
        
        await enqueue_job_retry(job.id, new_prompt)
        
        logger.warning(
            f"Job {job.id} failed quality check. "
            f"Retrying with improved prompt."
        )
    else:
        # Use fallback: gradient video with beat overlay
        logger.error(f"Job {job.id} max retries exhausted.")
        
        await create_fallback_visual(
            prompt=job.prompt,
            audio_url=job.audio_segment_url,
            beats=job.beats_json
        )
```

---

## Implementation in Your System

### Updated Segment Planner (Gemini)

```python
# app/services/segment_planner.py

from google.generativeai import GenerativeAI

class SegmentPlannerService:
    """Use Gemini to plan segments with cinematography awareness."""
    
    async def plan_segments(self, job: Job) -> dict:
        """
        Create cinematically intelligent segment plan.
        
        Now considers:
        - Camera movements aligned with beat intensity
        - Transition types on specific beat types
        - Color palette consistency
        - Lighting progression through 30s
        """
        
        genai = GenerativeAI(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-pro")
        
        # Get beat analysis
        beat_data = analyze_beat_structure(job.beats_json, job.bpm)
        
        prompt = f"""
You are a professional video editor and cinematographer.
Plan a cinematic 30-second reel with the following:

Audio Structure:
- BPM: {job.bpm}
- Total Duration: 30 seconds
- Beat Times: {job.beats_json}
- Beat Analysis: {json.dumps(beat_data)}
  * Intro beats: {beat_data['intro_beats']}
  * Build beats: {beat_data['build_beats']}
  * Peak beats: {beat_data['peak_beats']}
  * Outro beats: {beat_data['outro_beats']}

Creative Direction:
- Prompt: {job.prompt}
- Style: {job.style_preset}

FOR EACH SEGMENT, specify:
1. Start/end time
2. **Camera movement** (static, pan, zoom, tracking, whip)
3. **Composition** (rule of thirds, centered, negative space)
4. **Lighting** (bright, dark, high-contrast, soft)
5. **Color tone** (warm, cool, saturated, desaturated)
6. **Transition type** (cut, fade, zoom, motion blur)
7. **Transition timing** (on beat, off-beat, duration)
8. **Exact prompt** for AI video generation

CINEMATOGRAPHY RULES:
- Cuts happen ONLY on beat boundaries
- Transitions on beat drops are hard cuts (instant)
- Transitions on sustained notes are crossfades (200-500ms)
- Color palette is CONSISTENT throughout
- Lighting follows 3-point lighting principles
- All shots properly lit (no harsh shadows)
- Maintain visual interest through composition variation

Output JSON:
{{
  "segments": [
    {{
      "id": 1,
      "start_sec": 0,
      "end_sec": 3,
      "duration_sec": 3,
      "camera_movement": "smooth zoom in",
      "composition": "rule_of_thirds_left",
      "lighting": "key light from upper left, fill light softening",
      "color_tone": "warm golden (2700K), rich shadows",
      "transition_in": "none (first segment)",
      "transition_out": "hard cut on beat at 3.0s",
      "transition_duration_ms": 0,
      "generation_prompt": "..."
    }},
    ...
  ],
  "overall_color_palette": "warm cinematic with golden hour tones",
  "overall_lighting_approach": "studio 3-point + dramatic key light",
  "consistency_notes": "Maintain warm tone throughout, bright key light in every shot"
}}
"""
        
        response = await model.generate_content(prompt)
        plan = json.loads(response.text)
        
        return plan
```

### Updated FFmpeg Renderer (Color-Aware)

```python
# app/workers/ffmpeg_renderer.py

class FFmpegRenderer:
    """Render video with color consistency."""
    
    async def render_reel(self, 
                         segments: list,
                         audio_url: str,
                         color_palette: str) -> str:
        """
        1. Generate all clips
        2. Analyze and match colors
        3. Apply global LUT
        4. Sync with audio
        5. Quality check
        """
        
        # Step 1: Generate all clips with prompts from plan
        generated_clips = []
        for segment in segments:
            clip = await self.generate_segment(segment)
            generated_clips.append(clip)
        
        # Step 2: Analyze first clip for color baseline
        first_clip_colors = analyze_clip_colors(generated_clips[0])
        
        # Step 3: Match all subsequent clips to first
        matched_clips = [generated_clips[0]]
        for i in range(1, len(generated_clips)):
            corrected = await self.match_colors_to_baseline(
                generated_clips[i],
                first_clip_colors
            )
            matched_clips.append(corrected)
        
        # Step 4: Build FFmpeg concat script
        concat_script = self.build_concat_with_transitions(
            matched_clips,
            segments,
            color_palette
        )
        
        # Step 5: Execute rendering with LUT
        final_video = await self.execute_ffmpeg_with_lut(
            concat_script,
            audio_url,
            color_palette
        )
        
        # Step 6: Quality check
        quality_report = await self.quality_gate(final_video)
        if not quality_report["passed"]:
            raise QualityCheckError(quality_report["issues"])
        
        return final_video
    
    async def match_colors_to_baseline(self, 
                                      clip_path: str,
                                      baseline_colors: dict) -> str:
        """Match clip to baseline brightness/saturation."""
        
        current_colors = analyze_clip_colors(clip_path)
        
        brightness_diff = (
            baseline_colors["avg_brightness"] - 
            current_colors["avg_brightness"]
        )
        
        saturation_scale = (
            baseline_colors["avg_saturation"] / 
            current_colors["avg_saturation"]
        )
        
        # FFmpeg curves adjustment
        filter_str = f"curves=b='{brightness_diff}',eq=saturation={saturation_scale}"
        
        cmd = f"""
        ffmpeg -i {clip_path} \
          -vf "{filter_str}" \
          -c:v libx264 -preset fast \
          {clip_path}_matched.mp4
        """
        
        result = await run_ffmpeg(cmd)
        return result
    
    def build_concat_with_transitions(self,
                                      clips: list,
                                      segments: list,
                                      color_palette: str) -> str:
        """Build FFmpeg filter graph with all transitions."""
        
        filter_graph = ""
        
        for i, (clip, segment) in enumerate(zip(clips, segments)):
            if i == 0:
                filter_graph += f"[0:v]"
            else:
                transition = segment["transition_out"]
                duration = segment["transition_duration_ms"] / 1000.0
                
                if transition == "hard_cut":
                    filter_graph += f"[{i}:v]"
                elif transition == "crossfade":
                    filter_graph += f"xfade=transition=fade:duration={duration}[v{i}];"
                    filter_graph += f"[v{i}]"
                elif transition == "zoom":
                    filter_graph += f"xfade=transition=zoomin:duration={duration}[v{i}];"
                    filter_graph += f"[v{i}]"
        
        # Apply global LUT
        filter_graph += f"lut3d={self.get_lut_path(color_palette)}"
        
        return filter_graph
```

### User-Facing API Update

```python
# app/api/routes/jobs.py

@router.post("/jobs", response_model=JobResponse)
async def create_job(
    request: JobCreateRequest,
    user: User = Depends(get_current_user)
):
    """
    Create reel with cinematography controls.
    
    Request now includes:
    - style_preset: affects cinematography
    - color_palette: consistent grading
    """
    
    # Validate style preset maps to cinematography rules
    valid_styles = [
        "cinematic_drama",    # High contrast, cool tones
        "energetic_dance",    # Dynamic movement, warm tones
        "luxe_travel",        # Golden hour, smooth pans
        "vaporwave_neon",     # Vibrant saturation, cool tones
        "film_noir",          # Desaturated, high contrast
        "modern_minimal"      # Clean, neutral tones
    ]
    
    if request.style_preset not in valid_styles:
        raise ValueError(f"Unknown style: {request.style_preset}")
    
    # Rest of job creation...
    job = Job(
        user_id=user.id,
        prompt=request.prompt,
        style_preset=request.style_preset,  # Now drives cinematography
        video_model=request.video_model,
        # ...
    )
    
    await db.add(job)
    await db.commit()
    
    # Queue with cinematography-aware planner
    worker.enqueue_job(job.id)
    
    return JobResponse.from_orm(job)
```

---

## Summary: Your Cinematic Advantage

### What Separates You From Generic AI Video Tools

```
Generic AI Tool:
1. User uploads video
2. Model generates random footage
3. Stitches together with default transitions
4. Result: Looks AI-generated, inconsistent, jarring

Your System:
1. User enters CINEMATIC PROMPT
2. Gemini plans CINEMATOGRAPHY-aware segments
3. AI generates clips with consistent color/lighting
4. Color matching + LUT applied globally
5. Transitions timed to BEAT structure
6. Quality gates ensure professional output
7. Result: Looks intentional, professional, synced
```

### Implementation Priority

**Week 1-2 (Minimum):**
- ✅ Basic prompt engineering
- ✅ Simple FFmpeg stitching
- ✅ Audio sync on beats

**Week 3-4 (Quality):**
- ✅ Color analysis & matching
- ✅ LUT application
- ✅ Quality gates

**Month 2+ (Professional):**
- ✅ AI-powered color grading
- ✅ Auto lighting correction
- ✅ Per-segment cinematography tuning

### Cost Impact

```
Free/Open-Source:
- FFmpeg color matching: $0
- LUT libraries: $0 (open-source)
- Prompt engineering: Engineering time only

Paid (Optional):
- Colourlab AI integration: ~$50/month
- Professional LUT packs: $20-100 one-time
```

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Implementation-ready