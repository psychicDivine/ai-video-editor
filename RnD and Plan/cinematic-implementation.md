# Cinematic Video Generator: Integration Guide

**Implementation:** Python FastAPI + Gemini + FFmpeg  
**Goal:** Turn raw user input into professional, cinematic AI-generated reels  
**Timeline:** 2-3 weeks to full implementation

---

## Part 1: Cinematography-Aware Segment Planner

### 1.1 Updated Job Schema

```python
# app/schemas/job.py

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class StylePreset(str, Enum):
    """Cinematography styles with specific visual rules."""
    CINEMATIC_DRAMA = "cinematic_drama"      # High contrast, cool, slow
    ENERGETIC_DANCE = "energetic_dance"      # Dynamic, warm, fast cuts
    LUXE_TRAVEL = "luxe_travel"              # Golden hour, smooth, epic
    VAPORWAVE = "vaporwave_neon"             # Vibrant, cool, stylized
    FILM_NOIR = "film_noir"                  # B&W/desaturated, hard light
    MODERN_MINIMAL = "modern_minimal"        # Clean, neutral, geometric

class ColorPalette(str, Enum):
    """Color grading palettes."""
    WARM_CINEMATIC = "warm_cinematic"        # 2700K, golden, rich
    COOL_MOODY = "cool_moody"                # 5600K, blue/teal, moody
    VIBRANT_NEON = "vibrant_neon"            # High sat, complementary
    FILM_STOCK = "film_stock"                # Desaturated, film-like

class JobCreateRequest(BaseModel):
    """Request with cinematography controls."""
    
    # Audio & Timing
    audio_segment_url: str = Field(...)
    bpm: int = Field(..., ge=60, le=200)
    beats: List[float] = Field(...)
    
    # Creative Input
    prompt: str = Field(..., min_length=10, max_length=500)
    style_preset: StylePreset = Field(default=StylePreset.CINEMATIC_DRAMA)
    
    # Quality Controls
    video_model: str = Field("open-sora")
    model_quality: str = Field("standard", description="standard, hd, 4k")
    
    # Optional
    color_palette: Optional[ColorPalette] = Field(
        default=ColorPalette.WARM_CINEMATIC
    )
    aspect_ratio: str = Field("9:16")

class CinematographySegment(BaseModel):
    """One segment of the planned timeline."""
    
    id: int
    start_sec: float
    end_sec: float
    duration_sec: float
    
    # Visual direction
    camera_movement: str  # "smooth zoom in", "hard pan right", etc
    composition: str      # "rule_of_thirds_left", "centered", etc
    lighting: str         # Detailed lighting setup
    color_tone: str       # Color temperature and saturation guidance
    
    # Transitions
    transition_in: str    # "none", "crossfade", "hard_cut", "zoom"
    transition_out: str
    transition_duration_ms: int  # 0 = hard cut, 200-500 = fade
    
    # Beat sync
    beat_times_in_segment: List[float]
    cut_on_beat_sec: float  # When to cut this segment
    
    # AI Generation
    generation_prompt: str  # Actual prompt sent to video model

class SegmentPlan(BaseModel):
    """Complete timeline plan."""
    
    segments: List[CinematographySegment]
    overall_color_palette: str
    overall_lighting_approach: str
    consistency_notes: str  # What to maintain throughout
    expected_total_duration: float
```

### 1.2 Gemini-Powered Segment Planner

```python
# app/services/segment_planner.py

import json
import logging
from typing import List, Dict
import google.generativeai as genai
from app.schemas.job import (
    JobCreateRequest, 
    CinematographySegment,
    SegmentPlan
)

logger = logging.getLogger(__name__)

class SegmentPlannerService:
    """Use Gemini to plan cinematic segments."""
    
    STYLE_CINEMATOGRAPHY = {
        "cinematic_drama": {
            "camera": "smooth and deliberate",
            "lighting": "dramatic 3-point with strong key light",
            "color": "cool tones (5500K+), rich shadows, low saturation",
            "transitions": "slow dissolves and crossfades (300-500ms)",
            "composition": "symmetrical, centered, layered depth",
            "pacing": "slow, contemplative, every cut intentional",
            "mood": "serious, professional, cinematic"
        },
        "energetic_dance": {
            "camera": "dynamic - pans, zooms, whips",
            "lighting": "bright key light, minimal fill (high contrast)",
            "color": "warm tones (2700-3200K), saturated, dynamic",
            "transitions": "hard cuts on beats, motion blur (50-100ms)",
            "composition": "rule of thirds, off-center, energetic angles",
            "pacing": "fast, cuts on every 1-2 beats",
            "mood": "energetic, confident, show-stopping"
        },
        "luxe_travel": {
            "camera": "slow tracking shots, gentle parallax",
            "lighting": "golden hour backlighting, rim light, no harsh shadows",
            "color": "warm golden (3200K), saturated oranges/yellows, soft",
            "transitions": "slow dissolves (500ms+), no hard cuts",
            "composition": "leading lines, negative space, rule of thirds",
            "pacing": "slow, contemplative, wanderlust-inducing",
            "mood": "luxury, wanderlust, peace, discovery"
        },
        "vaporwave_neon": {
            "camera": "stylized movements, zoom on text/objects",
            "lighting": "neon/synthetic lighting, high saturation",
            "color": "cool neons (blues, magentas), desaturated backgrounds",
            "transitions": "sharp cuts, digital glitch effects (if supported)",
            "composition": "geometric, centered, symmetrical",
            "pacing": "varied, artistic, experimental",
            "mood": "retro-futuristic, artistic, surreal"
        },
        "film_noir": {
            "camera": "static or slow pans, dramatic angles",
            "lighting": "high contrast, strong shadows, dramatic key light",
            "color": "desaturated, cool tones, occasional color pops",
            "transitions": "hard cuts, occasional fade to black",
            "composition": "rule of thirds, strong shadows in frame",
            "pacing": "slow, deliberate, mysterious",
            "mood": "dramatic, mysterious, timeless"
        },
        "modern_minimal": {
            "camera": "static or very subtle movements",
            "lighting": "even, soft, no harsh shadows",
            "color": "neutral (4000K), low saturation, clean",
            "transitions": "subtle fades, no hard cuts",
            "composition": "centered, geometric, negative space",
            "pacing": "slow, clean, professional",
            "mood": "modern, clean, sophisticated"
        }
    }
    
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    async def plan_segments(self, 
                           request: JobCreateRequest) -> SegmentPlan:
        """
        Plan entire 30-second reel with cinematography awareness.
        
        Returns structured segment plan with:
        - Start/end times
        - Camera movements
        - Lighting setups
        - Transitions timed to beats
        - AI generation prompts
        """
        
        # Analyze beat structure
        beat_structure = self._analyze_beats(request.beats, request.bpm)
        
        # Get cinematography rules for this style
        cine_rules = self.STYLE_CINEMATOGRAPHY[request.style_preset]
        
        # Build the planning prompt
        planning_prompt = self._build_planning_prompt(
            request=request,
            beat_structure=beat_structure,
            cinematography_rules=cine_rules
        )
        
        logger.info(f"Sending planning prompt to Gemini...")
        
        # Get plan from Gemini
        response = await self.model.generate_content(planning_prompt)
        plan_json = self._extract_json(response.text)
        
        # Convert to structured plan
        segment_plan = self._parse_plan_response(plan_json)
        
        logger.info(
            f"Generated plan with {len(segment_plan.segments)} segments"
        )
        
        return segment_plan
    
    def _analyze_beats(self, 
                       beats: List[float], 
                       bpm: int) -> Dict:
        """
        Analyze beat structure to identify:
        - Intro beats (first 3-4 seconds)
        - Build beats (acceleration)
        - Peak beats (climax, strongest hits)
        - Outro beats (resolution)
        """
        
        beat_interval = 60.0 / bpm  # seconds between beats
        
        # Identify beat density and intensity
        intro_beats = [b for b in beats if b < 4]
        build_beats = [b for b in beats if 4 <= b < 12]
        peak_beats = [b for b in beats if 12 <= b < 24]
        outro_beats = [b for b in beats if b >= 24]
        
        # Detect patterns
        beat_gaps = [beats[i+1] - beats[i] for i in range(len(beats)-1)]
        avg_gap = sum(beat_gaps) / len(beat_gaps) if beat_gaps else 0
        
        return {
            "bpm": bpm,
            "beat_interval": beat_interval,
            "total_beats": len(beats),
            "beat_times": beats,
            "intro_beats": intro_beats,
            "build_beats": build_beats,
            "peak_beats": peak_beats,
            "outro_beats": outro_beats,
            "avg_beat_gap": avg_gap,
            "has_acceleration": max(beat_gaps) > avg_gap * 1.5 if beat_gaps else False
        }
    
    def _build_planning_prompt(self, 
                              request: JobCreateRequest,
                              beat_structure: Dict,
                              cinematography_rules: Dict) -> str:
        """Build detailed prompt for Gemini to plan segments."""
        
        prompt = f"""
You are a professional video editor and cinematographer planning a 30-second music video.

TASK: Create a detailed, beat-synced segment plan for an AI video generator.

USER CREATIVE DIRECTION:
- Prompt: "{request.prompt}"
- Style: {request.style_preset.value}
- Color Palette: {request.color_palette if hasattr(request, 'color_palette') else 'warm_cinematic'}

MUSIC STRUCTURE:
- BPM: {beat_structure['bpm']}
- Total Beats: {beat_structure['total_beats']}
- Intro Beats (0-4s): {len(beat_structure['intro_beats'])} beats
- Build Phase (4-12s): {len(beat_structure['build_beats'])} beats  
- Peak Phase (12-24s): {len(beat_structure['peak_beats'])} beats
- Outro Phase (24-30s): {len(beat_structure['outro_beats'])} beats
- Beat Times: {beat_structure['beat_times']}

CINEMATOGRAPHY RULES FOR "{request.style_preset.value}":
- Camera: {cinematography_rules['camera']}
- Lighting: {cinematography_rules['lighting']}
- Color: {cinematography_rules['color']}
- Transitions: {cinematography_rules['transitions']}
- Composition: {cinematography_rules['composition']}
- Pacing: {cinematography_rules['pacing']}
- Mood: {cinematography_rules['mood']}

REQUIREMENTS FOR EACH SEGMENT:
1. Start and end times must snap to beat boundaries
2. Transitions must happen ON BEAT TIMES (not random)
3. Hard cuts (0ms) on high-energy beats
4. Crossfades (300-500ms) on sustained notes
5. Camera movement must match beat intensity
6. Color and lighting MUST BE CONSISTENT throughout
7. All shots properly lit (no underexposed areas)
8. Each segment is independently generatable by a text-to-video model

OUTPUT: Valid JSON ONLY (no markdown, no explanation).

{{
  "segments": [
    {{
      "id": 1,
      "start_sec": 0,
      "end_sec": 3,
      "duration_sec": 3,
      "camera_movement": "zoom in slowly from wide to medium shot",
      "composition": "rule_of_thirds_left",
      "lighting": "Key light from upper left at 45°, fill light softening shadows, bright overall",
      "color_tone": "warm golden (2700K), rich shadows, saturated warm tones",
      "transition_in": "none",
      "transition_out": "hard_cut",
      "transition_duration_ms": 0,
      "cut_on_beat_sec": 3.0,
      "beat_times_in_segment": [0.0, 1.0, 2.0],
      "generation_prompt": "Professional cinematic introduction. [detailed camera/lighting/color directions]. Character/object positioned at left 1/3. Golden warm lighting (2700K). 3 second duration. Vertical 1080x1920 resolution."
    }},
    {{
      "id": 2,
      "start_sec": 3,
      "end_sec": 7,
      "duration_sec": 4,
      "camera_movement": "dynamic pan right with zoom",
      "composition": "centered_rule_of_thirds_right",
      "lighting": "High contrast key light from right, minimal fill, dramatic",
      "color_tone": "warm tones slightly elevated, increased saturation",
      "transition_in": "hard_cut",
      "transition_out": "crossfade",
      "transition_duration_ms": 300,
      "cut_on_beat_sec": 7.0,
      "beat_times_in_segment": [3.0, 4.0, 5.0, 6.0],
      "generation_prompt": "Build energy phase. Dynamic camera movement panning right with slow zoom in. Warm lighting with elevated saturation. High-energy action. Vertical 1080x1920 resolution."
    }}
  ],
  "overall_color_palette": "Warm cinematic: consistent 2700-3200K throughout, golden tones, rich shadows never pure black",
  "overall_lighting_approach": "Professional 3-point lighting in every shot: key light, fill light for shadow detail, back light for separation",
  "consistency_notes": "Maintain warm tone and bright key light in every segment. No sudden color shifts. All transitions on beat boundaries. Saturation increases from intro to peak, then calms in outro."
}}

CRITICAL RULES:
- ALL transitions must be ON BEAT TIMES from the beat_times array above
- NO floating transitions at random times
- Color and lighting must be consistent to avoid jarring cuts
- Each segment must be independently generatable
- Total duration must equal exactly 30 seconds
"""
        
        return prompt
    
    def _extract_json(self, response_text: str) -> Dict:
        """Extract JSON from Gemini response (might have markdown)."""
        
        # Try to find JSON block
        if "```json" in response_text:
            start = response_text.index("```json") + 7
            end = response_text.index("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.index("```") + 3
            end = response_text.index("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text
        
        return json.loads(json_str)
    
    def _parse_plan_response(self, plan_json: Dict) -> SegmentPlan:
        """Convert Gemini JSON response to SegmentPlan."""
        
        segments = []
        for seg_data in plan_json["segments"]:
            segment = CinematographySegment(
                id=seg_data["id"],
                start_sec=seg_data["start_sec"],
                end_sec=seg_data["end_sec"],
                duration_sec=seg_data["duration_sec"],
                camera_movement=seg_data["camera_movement"],
                composition=seg_data["composition"],
                lighting=seg_data["lighting"],
                color_tone=seg_data["color_tone"],
                transition_in=seg_data["transition_in"],
                transition_out=seg_data["transition_out"],
                transition_duration_ms=seg_data["transition_duration_ms"],
                beat_times_in_segment=seg_data["beat_times_in_segment"],
                cut_on_beat_sec=seg_data["cut_on_beat_sec"],
                generation_prompt=seg_data["generation_prompt"]
            )
            segments.append(segment)
        
        return SegmentPlan(
            segments=segments,
            overall_color_palette=plan_json["overall_color_palette"],
            overall_lighting_approach=plan_json["overall_lighting_approach"],
            consistency_notes=plan_json["consistency_notes"],
            expected_total_duration=sum(s.duration_sec for s in segments)
        )
```

---

## Part 2: Color Matching & LUT Application

### 2.1 Color Analysis Service

```python
# app/services/color_grading.py

import cv2
import numpy as np
import subprocess
import logging
from typing import Dict, Tuple
import os

logger = logging.getLogger(__name__)

class ColorAnalysisService:
    """Analyze video colors to ensure consistency."""
    
    def analyze_clip(self, video_path: str, sample_frames: int = 30) -> Dict:
        """
        Analyze color distribution in a video clip.
        
        Returns:
        - average_brightness (0-255)
        - average_saturation (0-100)
        - average_hue (0-180)
        - variance metrics (std deviation)
        - dominant_colors
        """
        
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        brightness_values = []
        saturation_values = []
        hue_values = []
        
        while frame_count < sample_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            brightness_values.append(np.mean(hsv[:,:,2]))
            saturation_values.append(np.mean(hsv[:,:,1]))
            hue_values.append(np.mean(hsv[:,:,0]))
            
            frame_count += 1
        
        cap.release()
        
        return {
            "avg_brightness": float(np.mean(brightness_values)),
            "avg_saturation": float(np.mean(saturation_values)),
            "avg_hue": float(np.mean(hue_values)),
            "brightness_std": float(np.std(brightness_values)),
            "saturation_std": float(np.std(saturation_values)),
            "brightness_min": float(np.min(brightness_values)),
            "brightness_max": float(np.max(brightness_values)),
            "frame_count": frame_count
        }
    
    def detect_color_shift(self, 
                          clip1_colors: Dict,
                          clip2_colors: Dict) -> Dict:
        """
        Detect if two clips have significant color differences.
        
        Returns adjustment factors needed.
        """
        
        brightness_diff = clip1_colors["avg_brightness"] - clip2_colors["avg_brightness"]
        saturation_ratio = (
            clip1_colors["avg_saturation"] / 
            (clip2_colors["avg_saturation"] + 1e-6)
        )
        
        needs_correction = {
            "brightness": abs(brightness_diff) > 10,
            "saturation": abs(1.0 - saturation_ratio) > 0.15
        }
        
        return {
            "brightness_diff": brightness_diff,
            "saturation_ratio": saturation_ratio,
            "needs_correction": any(needs_correction.values()),
            "corrections_needed": needs_correction
        }
    
    def generate_correction_filter(self,
                                  target_brightness: float,
                                  target_saturation: float,
                                  current_colors: Dict) -> str:
        """
        Generate FFmpeg filter string to match colors.
        
        Uses curves and EQ filters.
        """
        
        brightness_diff = target_brightness - current_colors["avg_brightness"]
        sat_scale = target_saturation / (current_colors["avg_saturation"] + 1e-6)
        
        # Create curves adjustment (brightness)
        if brightness_diff > 0:
            # Brighten
            curve_str = f"curves=v='0/0 255/{255+int(brightness_diff)}'"
        else:
            # Darken
            curve_str = f"curves=v='0/0 255/{255+int(brightness_diff)}'"
        
        # Create saturation adjustment
        eq_str = f"eq=saturation={sat_scale}"
        
        return f"{curve_str},{eq_str}"

class ColorMatchingService:
    """Match all clips to first clip's colors."""
    
    def __init__(self):
        self.analyzer = ColorAnalysisService()
    
    async def match_all_clips(self,
                             clip_paths: list) -> list:
        """
        1. Analyze first clip
        2. Match all others to it
        3. Return corrected clip paths
        """
        
        # Get baseline colors from first clip
        baseline_colors = self.analyzer.analyze_clip(clip_paths[0])
        logger.info(f"Baseline colors: {baseline_colors}")
        
        matched_clips = [clip_paths[0]]  # First is already baseline
        
        for i, clip_path in enumerate(clip_paths[1:], 1):
            current_colors = self.analyzer.analyze_clip(clip_path)
            
            # Check if correction needed
            shift = self.analyzer.detect_color_shift(baseline_colors, current_colors)
            
            if shift["needs_correction"]:
                logger.info(f"Clip {i} needs color correction: {shift}")
                
                filter_str = self.analyzer.generate_correction_filter(
                    target_brightness=baseline_colors["avg_brightness"],
                    target_saturation=baseline_colors["avg_saturation"],
                    current_colors=current_colors
                )
                
                corrected_path = await self._apply_color_correction(
                    clip_path, 
                    filter_str
                )
                matched_clips.append(corrected_path)
            else:
                logger.info(f"Clip {i} color matches baseline, no correction needed")
                matched_clips.append(clip_path)
        
        return matched_clips
    
    async def _apply_color_correction(self, 
                                     video_path: str,
                                     filter_str: str) -> str:
        """Apply FFmpeg color correction filter."""
        
        output_path = video_path.replace(".mp4", "_corrected.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", filter_str,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Color correction failed: {result.stderr}")
            raise Exception("FFmpeg color correction failed")
        
        logger.info(f"Color corrected: {output_path}")
        return output_path

class LUTService:
    """Apply Look-Up Tables for consistent color grading."""
    
    def __init__(self):
        self.luts_dir = "/app/luts"
        self.available_luts = self._load_available_luts()
    
    def _load_available_luts(self) -> Dict:
        """Load available LUT files."""
        
        luts = {}
        
        if os.path.exists(self.luts_dir):
            for filename in os.listdir(self.luts_dir):
                if filename.endswith(".cube"):
                    style = filename.replace(".cube", "")
                    luts[style] = os.path.join(self.luts_dir, filename)
        
        # Fallback to default open-source LUTs
        if not luts:
            luts = {
                "cinematic": "cinematic.cube",
                "warm": "warm_golden.cube",
                "cool": "cool_blue.cube",
                "vibrant": "vibrant.cube"
            }
        
        return luts
    
    async def apply_lut_to_video(self,
                                video_path: str,
                                style: str) -> str:
        """Apply LUT to entire video for consistent color."""
        
        if style not in self.available_luts:
            logger.warning(f"LUT '{style}' not found, using default")
            style = "cinematic"
        
        lut_path = self.available_luts[style]
        output_path = video_path.replace(".mp4", f"_lut_{style}.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"lut3d={lut_path}:interp=tetrahedral",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"LUT application failed: {result.stderr}")
            raise Exception("FFmpeg LUT application failed")
        
        logger.info(f"LUT applied ({style}): {output_path}")
        return output_path
```

---

## Part 3: FFmpeg Rendering with Color Consistency

### 3.1 Enhanced FFmpeg Renderer

```python
# app/workers/ffmpeg_renderer.py

import subprocess
import json
import logging
import os
from typing import List, Dict
from app.services.color_grading import ColorMatchingService, LUTService
from app.schemas.job import CinematographySegment, SegmentPlan

logger = logging.getLogger(__name__)

class FFmpegRenderer:
    """Render complete reel with color consistency."""
    
    def __init__(self):
        self.color_matcher = ColorMatchingService()
        self.lut_service = LUTService()
    
    async def render_reel(self,
                         segments: List[CinematographySegment],
                         segment_plan: SegmentPlan,
                         audio_url: str,
                         output_path: str,
                         color_palette: str) -> str:
        """
        Complete rendering pipeline:
        1. Generate all clips
        2. Match colors
        3. Apply LUT
        4. Build concat with transitions
        5. Sync audio
        6. Quality check
        """
        
        logger.info(f"Starting reel render with {len(segments)} segments")
        
        # Step 1: Generate clips from segment prompts
        generated_clips = []
        for segment in segments:
            clip = await self._generate_segment(segment)
            generated_clips.append(clip)
        
        # Step 2: Match colors to first clip
        logger.info("Matching colors across clips...")
        matched_clips = await self.color_matcher.match_all_clips(generated_clips)
        
        # Step 3: Apply global LUT for consistent look
        logger.info(f"Applying LUT ({color_palette})...")
        lut_clips = []
        for clip in matched_clips:
            lut_clip = await self.lut_service.apply_lut_to_video(clip, color_palette)
            lut_clips.append(lut_clip)
        
        # Step 4: Build concat with transitions
        logger.info("Building concat file with transitions...")
        concat_content = self._build_concat_file(
            lut_clips, 
            segments,
            segment_plan
        )
        
        concat_file = "/tmp/concat_list.txt"
        with open(concat_file, "w") as f:
            f.write(concat_content)
        
        # Step 5: Render with audio sync
        logger.info("Rendering final video...")
        final_video = await self._render_with_audio(
            concat_file,
            audio_url,
            output_path,
            segment_plan
        )
        
        # Step 6: Quality check
        logger.info("Running quality checks...")
        quality_ok = await self._quality_check(final_video)
        
        if not quality_ok:
            logger.error("Quality check failed!")
            raise Exception("Quality check failed")
        
        logger.info(f"Reel rendered successfully: {final_video}")
        return final_video
    
    async def _generate_segment(self, segment: CinematographySegment) -> str:
        """Generate a single segment using video model."""
        
        # This calls the video model provider
        # For now, placeholder - integrate with your model provider
        
        output_path = f"/tmp/segment_{segment.id}.mp4"
        
        # TODO: Call actual video model with segment.generation_prompt
        # model_provider.generate(prompt=segment.generation_prompt, duration=segment.duration_sec)
        
        logger.info(f"Generated segment {segment.id}: {output_path}")
        return output_path
    
    def _build_concat_file(self,
                          clips: List[str],
                          segments: List[CinematographySegment],
                          plan: SegmentPlan) -> str:
        """
        Build FFmpeg concat demuxer file with transitions.
        
        Format:
        file 'clip1.mp4'
        duration 3
        file 'clip2.mp4'
        duration 4
        ...
        """
        
        concat_lines = []
        
        for clip, segment in zip(clips, segments):
            concat_lines.append(f"file '{clip}'")
            concat_lines.append(f"duration {segment.duration_sec}")
        
        return "\n".join(concat_lines)
    
    async def _render_with_audio(self,
                                concat_file: str,
                                audio_url: str,
                                output_path: str,
                                plan: SegmentPlan) -> str:
        """
        Render final video:
        1. Concat video clips
        2. Add audio
        3. Ensure proper format (H.264, AAC)
        """
        
        # First, concat video without audio
        temp_video = output_path.replace(".mp4", "_temp.mp4")
        
        # Build filter graph for transitions
        filter_graph = self._build_transition_filters(plan)
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-filter_complex", filter_graph,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            temp_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Concat failed: {result.stderr}")
            raise Exception("FFmpeg concat failed")
        
        # Now add audio
        cmd = [
            "ffmpeg",
            "-i", temp_video,
            "-i", audio_url,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Audio mixing failed: {result.stderr}")
            raise Exception("FFmpeg audio mixing failed")
        
        # Cleanup temp
        os.remove(temp_video)
        
        return output_path
    
    def _build_transition_filters(self, plan: SegmentPlan) -> str:
        """Build FFmpeg filter graph for all transitions."""
        
        if len(plan.segments) == 1:
            return "[0:v]format=yuv420p[out]"
        
        # For simplicity, use concat demuxer transitions
        # More complex transitions would use xfade filter
        
        filter_parts = []
        
        for i, segment in enumerate(plan.segments):
            if segment.transition_out == "hard_cut":
                # No transition, just concatenate
                pass
            elif segment.transition_out == "crossfade":
                # xfade creates crossfade between clips
                duration = segment.transition_duration_ms / 1000.0
                filter_parts.append(f"[{i}:v][{i+1}:v]xfade=transition=fade:duration={duration}[v{i}];")
        
        if filter_parts:
            return "".join(filter_parts) + "[v" + str(len(plan.segments)-2) + "]format=yuv420p[out]"
        else:
            return "[0:v]format=yuv420p[out]"
    
    async def _quality_check(self, video_path: str) -> bool:
        """Run quality checks on final video."""
        
        checks = {
            "duration": False,
            "resolution": False,
            "codec": False,
            "audio": False
        }
        
        # Get video info with ffprobe
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration,width,height,codec_name",
            "-of", "json",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        stream = info["streams"][0]
        
        # Check duration (should be ~30 seconds)
        checks["duration"] = 25 < float(stream.get("duration", 0)) < 35
        
        # Check resolution
        checks["resolution"] = (
            stream.get("width") == 1080 and 
            stream.get("height") == 1920
        )
        
        # Check codec
        checks["codec"] = stream.get("codec_name") == "h264"
        
        # Check audio exists
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name",
            "-of", "json",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        audio_info = json.loads(result.stdout)
        checks["audio"] = len(audio_info.get("streams", [])) > 0
        
        all_passed = all(checks.values())
        
        logger.info(f"Quality checks: {checks}")
        
        return all_passed
```

---

## Part 4: Integration into Job Worker

### 4.1 Updated Job Worker

```python
# app/workers/worker.py

import logging
from app.services.segment_planner import SegmentPlannerService
from app.workers.ffmpeg_renderer import FFmpegRenderer
from app.database import SessionLocal
from app import models

logger = logging.getLogger(__name__)

class JobWorker:
    """Main job orchestration worker."""
    
    def __init__(self):
        self.planner = SegmentPlannerService()
        self.renderer = FFmpegRenderer()
    
    async def process_job(self, job_id: str):
        """
        Process complete reel generation:
        1. Plan cinematography-aware segments
        2. Generate video clips
        3. Match colors
        4. Apply LUT
        5. Render with audio sync
        """
        
        db = SessionLocal()
        
        try:
            # Get job from database
            job = db.query(models.Job).filter(
                models.Job.id == job_id
            ).first()
            
            if not job:
                logger.error(f"Job not found: {job_id}")
                return
            
            # Update status
            job.status = "planning"
            db.commit()
            
            # Step 1: Plan cinematography segments
            logger.info(f"Planning segments for job {job_id}...")
            
            request = self._build_request_from_job(job)
            segment_plan = await self.planner.plan_segments(request)
            
            # Save plan to job
            job.timeline_plan = segment_plan.dict()
            job.status = "rendering"
            db.commit()
            
            # Step 2-5: Render complete reel
            logger.info(f"Rendering reel for job {job_id}...")
            
            final_video_path = await self.renderer.render_reel(
                segments=segment_plan.segments,
                segment_plan=segment_plan,
                audio_url=job.audio_segment_url,
                output_path=f"/tmp/{job_id}_final.mp4",
                color_palette=job.color_palette or "warm_cinematic"
            )
            
            # Step 3: Upload to S3/Spaces
            final_url = await self._upload_to_storage(final_video_path)
            
            # Update job with final result
            job.status = "done"
            job.final_video_url = final_url
            job.completed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Job {job_id} completed: {final_url}")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        finally:
            db.close()
    
    def _build_request_from_job(self, job: models.Job) -> "JobCreateRequest":
        """Convert Job model to JobCreateRequest."""
        
        from app.schemas.job import JobCreateRequest, StylePreset, ColorPalette
        
        return JobCreateRequest(
            audio_segment_url=job.audio_segment_url,
            bpm=job.bpm,
            beats=job.beats_json,
            prompt=job.prompt,
            style_preset=StylePreset(job.style_preset) if job.style_preset else StylePreset.CINEMATIC_DRAMA,
            video_model=job.video_model,
            model_quality=job.model_quality,
            color_palette=ColorPalette(job.color_palette) if job.color_palette else ColorPalette.WARM_CINEMATIC
        )
    
    async def _upload_to_storage(self, video_path: str) -> str:
        """Upload rendered video to S3/Spaces."""
        
        # TODO: Implement S3 upload
        # For now, return local path
        return video_path
```

---

## Implementation Checklist

### Phase 1 (Week 1): Setup
- [ ] Create Schema classes (cinematic-aware)
- [ ] Implement SegmentPlannerService with Gemini
- [ ] Test Gemini planning with sample prompts
- [ ] Verify JSON parsing from Gemini responses

### Phase 2 (Week 2): Color Management
- [ ] Implement ColorAnalysisService
- [ ] Implement ColorMatchingService
- [ ] Implement LUTService
- [ ] Download/prepare LUT files
- [ ] Test color matching pipeline

### Phase 3 (Week 3): Rendering
- [ ] Implement FFmpegRenderer
- [ ] Test clip generation (using dummy videos initially)
- [ ] Test concat with transitions
- [ ] Test audio sync
- [ ] Implement quality checks

### Phase 4 (Week 4+): Integration & Testing
- [ ] Integrate SegmentPlanner → FFmpegRenderer → Worker
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Deploy to staging

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Ready for implementation