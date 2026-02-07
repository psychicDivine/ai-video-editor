try:
    import google.generativeai as genai
except Exception:
    genai = None

import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import shutil
import subprocess
from app.config import settings

logger = logging.getLogger(__name__)

class BaseDirector(ABC):
    """Abstract base class for AI Directors (Gemini, Local, etc.)"""
    
    @abstractmethod
    def find_viral_clips(self, video_path: str, style: str = "viral_hooks") -> Dict[str, Any]:
        """Returns { 'clips': List[Dict], 'metadata': Dict }"""
        pass

    def prepare_proxy(self, video_path: str, output_path: str) -> bool:
        """
        Creates a lightweight 'AI Proxy' video (240p @ 1fps).
        Returns True if successful.
        """
        try:
            # Expert FFmpeg command for tiny proxy
            # scale=-2:240 -> Keep aspect ratio, height 240, width must be even
            # fps=1 -> One frame per second
            # crf 32 -> High compression (low quality is fine for AI)
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", "scale=-2:240,fps=1",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "32",
                "-c:a", "aac", "-ar", "22050", "-ac", "1", "-b:a", "32k",
                output_path
            ]
            
            logger.info(f"Generating AI Proxy: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.error(f"Failed to create proxy: {e}")
            return False

class GeminiDirector(BaseDirector):
    """
    AI Director implementation using Google Gemini 1.5 Pro/Flash.
    """
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use Flash for speed/cost
            self.model_name = 'gemini-flash-latest' 
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Gemini API key not found.")
            self.model = None

    def upload_to_gemini(self, video_path: str) -> Any:
        """Uploads a video file to Gemini File API."""
        if not self.model:
            return None
            
        logger.info(f"Uploading {video_path} to Gemini...")
        video_file = genai.upload_file(path=video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            logger.info(f"Gemini is processing video {video_file.name}...")
            time.sleep(5)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            logger.error("Video processing failed in Gemini.")
            return None
            
        logger.info(f"Video uploaded successfully: {video_file.uri}")
        return video_file

    def get_ai_cuts(self, video_paths: List[str], style: str, target_duration: float) -> List[Dict[str, float]]:
        """Legacy method for Music Video cuts"""
        if not self.model:
            logger.info("No API key, skipping AI analysis.")
            return []

        try:
            # For MVP, we'll just analyze the first video (or we could concat them first).
            # Uploading multiple large files takes time, so let's start with the first one 
            # as the "B-roll" source.
            source_video = video_paths[0]
            video_file = self.upload_to_gemini(source_video)
            
            if not video_file:
                return []

            prompt = f"""
            You are a professional video editor. I need to create a {style} style video that is exactly {target_duration} seconds long.
            
            Watch this video footage and select the absolute best {int(target_duration/4)} clips.
            Each clip should be between 3 and 5 seconds long.
            Focus on: stable shots, clear action, good lighting, and interesting composition.
            
            Return ONLY a JSON list of cuts. Format:
            [
                {{"start": 10.5, "end": 14.5, "description": "man running"}},
                {{"start": 45.0, "end": 49.0, "description": "sunset view"}}
            ]
            
            Do not include any markdown formatting, just the raw JSON string.
            """
            
            logger.info("Asking Gemini for cuts...")
            response = self.model.generate_content([video_file, prompt])
            
            # Clean up cleanup response text
            text = response.text.replace('```json', '').replace('```', '').strip()
            cuts = json.loads(text)
            
            # Format for processor (add source_index)
            formatted_cuts = []
            for cut in cuts:
                formatted_cuts.append({
                    "source_index": 0, # Assuming single source for MVP
                    "start": float(cut["start"]),
                    "end": float(cut["end"])
                })
                
            logger.info(f"Gemini returned {len(formatted_cuts)} cuts.")
            
            # Cleanup remote file
            try:
                genai.delete_file(video_file.name)
                logger.info(f"Deleted remote file {video_file.name}")
            except Exception:
                pass
            
            return formatted_cuts

            return formatted_cuts

        except Exception as e:
            logger.error(f"Error in AI Director: {e}")
            return []

    def find_viral_clips(self, video_path: str, style: str = "viral_hooks") -> Dict[str, Any]:
        """
        Analyzes video to find viral short-form segments.
        Returns: { 'clips': [], 'metadata': { 'director': 'gemini', ... } }
        """
        result = {
            "clips": [],
            "metadata": {
                "director": "gemini",
                "model": self.model_name if self.model else None,
                "status": "skipped",
                "reason": ""
            }
        }
        
        if not self.model:
            result["metadata"]["reason"] = "No API key found"
            logger.info("No API key, skipping Gemini analysis.")
            return result

        try:
             # Check file size, if > 50MB warn (should rely on proxy)
            if Path(video_path).stat().st_size > 50 * 1024 * 1024:
                logger.warning(f"Uploading large file ({Path(video_path).stat().st_size/1024/1024:.1f}MB) to Gemini. Consider using proxy.")

            video_file = self.upload_to_gemini(video_path)
            if not video_file:
                result["metadata"]["status"] = "failed"
                result["metadata"]["reason"] = "Upload to Gemini failed"
                return result

            prompt = f"""
            You are a social media expert and professional viral video editor. 
            Watch this video and identify the top 5 most engaging, high-impact "viral" moments suitable for TikTok, Reels, and YouTube Shorts.

            IMPORTANT INSTRUCTIONS:
            - Aim for exactly 5 clips if the video duration allows.
            - Length: 30 to 60 seconds each.
            - Diversity: DO NOT just pick the beginning of the video. Look for the most intense, funny, or insightful moments across the ENTIRE duration.
            - Content: Look for clear facial expressions, high-energy talking, laughter, or dramatic statements.
            - Lead-in: Ensure each clip starts slightly before a major point or statement to provide context.

            Return ONLY a raw JSON list. Format:
            [
                {{"start": 10.5, "end": 45.2, "summary": "Discussion about AI safety", "reason": "Strong hook and polarizing statement"}},
                {{"start": 300.2, "end": 355.0, "summary": "Funny anecdote about coding", "reason": "Contagious laughter and relatable content"}},
                ...
            ]
            """
            
            logger.info("Asking Gemini for viral clips...")
            response = self.model.generate_content([video_file, prompt])
            
            # Clean up response text
            text = response.text.replace('```json', '').replace('```', '').strip()
            # Handle potential extra text
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                text = text[start_idx:end_idx]

            clips = json.loads(text)
            
            logger.info(f"Gemini found {len(clips)} viral clips.")
            
            try:
                genai.delete_file(video_file.name)
            except Exception:
                pass
            
            result["clips"] = clips
            result["metadata"]["status"] = "success"
            return result

        except Exception as e:
            logger.error(f"Error finding viral clips: {e}")
            result["metadata"]["status"] = "error"
            result["metadata"]["reason"] = str(e)
            return result

class LocalDirector(BaseDirector):
    """
    AI Director that uses local signal processing (librosa) 
    to find interesting moments based on audio energy.
    """
    def find_viral_clips(self, video_path: str, style: str = "viral_hooks") -> Dict[str, Any]:
        import librosa
        import numpy as np
        from scipy.signal import find_peaks

        logger.info(f"Using LocalDirector (Audio Energy) for {video_path}")
        
        result = {
            "clips": [],
            "metadata": {
                "director": "local_audio",
                "status": "init",
                "reason": ""
            }
        }

        try:
            # 1. Extract audio to a temporary WAV for reliable loading
            from app.services.ffmpeg_handler import FFmpegHandler
            ffmpeg = FFmpegHandler()
            
            temp_audio = Path(video_path).parent / "temp_analysis_audio.wav"
            if not ffmpeg.trim_audio(video_path, str(temp_audio), 0, 3600): # Extract all
                logger.error("Failed to extract audio for LocalDirector")
                return result

            # 2. Load audio from temporary WAV
            try:
                y, sr = librosa.load(str(temp_audio), sr=22050)
            finally:
                if temp_audio.exists():
                    temp_audio.unlink()
            
            # 3. Calculate RMS energy
            hop_length = 512
            energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]
            
            # 3. Find peaks (loud segments)
            energy = (energy - np.min(energy)) / (np.max(energy) + 1e-6)
            fps = sr / hop_length
            min_dist = int(30 * fps)
            
            peaks, _ = find_peaks(energy, height=0.5, distance=min_dist)
            
            if len(peaks) == 0:
                result["metadata"]["status"] = "skipped"
                result["metadata"]["reason"] = "No energy peaks detected"
                return result

            # 4. Convert peaks to clips (30-60s)
            clips = []
            duration = librosa.get_duration(y=y, sr=sr)
            peak_energies = energy[peaks]
            top_indices = np.argsort(peak_energies)[-3:][::-1]
            top_peaks = peaks[top_indices]
            
            for peak in top_peaks:
                peak_time = peak / fps
                start = max(0, peak_time - 15)
                end = min(duration, start + 45)
                
                clips.append({
                    "start": float(start),
                    "end": float(end),
                    "summary": f"High energy segment at {int(peak_time)}s",
                    "reason": "Audio energy peak detected"
                })
            
            result["clips"] = sorted(clips, key=lambda x: x['start'])
            result["metadata"]["status"] = "success"
            result["metadata"]["peak_count"] = len(peaks)
            return result

        except Exception as e:
            logger.error(f"LocalDirector failed: {e}")
            result["metadata"]["status"] = "error"
            result["metadata"]["reason"] = str(e)
            return result

class RandomDirector(BaseDirector):
    """
    Emergency fallback director that just picks segments from the video.
    """
    def find_viral_clips(self, video_path: str, style: str = "viral_hooks") -> Dict[str, Any]:
        logger.info("Using RandomDirector fallback")
        result = {
            "clips": [],
            "metadata": {
                "director": "random",
                "status": "success",
                "reason": "AI models failed or disabled"
            }
        }
        try:
            from app.services.ffmpeg_handler import FFmpegHandler
            ffmpeg = FFmpegHandler()
            info = ffmpeg.get_video_info(video_path)
            duration = info.get("duration", 60.0)
            
            start = duration / 2
            result["clips"] = [{
                "start": max(0, start - 30),
                "end": min(duration, start + 30),
                "summary": "Middle Segment (Random Fallback)",
                "reason": "No AI models available"
            }]
            return result
        except Exception as e:
            logger.error(f"RandomDirector failed: {e}")
            result["metadata"]["status"] = "error"
            result["metadata"]["reason"] = str(e)
            return result

class AIDirector:
    """
    Orchestrator that tries different directors in order of quality.
    """
    def __init__(self):
        self.gemini = GeminiDirector()
        self.local = LocalDirector()
        self.random = RandomDirector()
        # Track full history of attempts
        self.history = []
        
    def prepare_proxy(self, video_path: str, output_path: str) -> bool:
        return self.gemini.prepare_proxy(video_path, output_path)

    def find_viral_clips(self, video_path: str, style: str = "viral_hooks") -> List[Dict[str, Any]]:
        """
        Unified entry point. 
        Note: We return List[Dict] for backward compatibility with VideoProcessor for now,
        but we store the metadata in self.history.
        """
        self.history = []
        
        # 1. Try Gemini
        res_gemini = self.gemini.find_viral_clips(video_path, style)
        self.history.append(res_gemini["metadata"])
        if res_gemini["clips"]:
            return res_gemini["clips"]
        
        # 2. Try Local
        res_local = self.local.find_viral_clips(video_path, style)
        self.history.append(res_local["metadata"])
        if res_local["clips"]:
            return res_local["clips"]
            
        # 3. Fallback to Random
        res_random = self.random.find_viral_clips(video_path, style)
        self.history.append(res_random["metadata"])
        return res_random["clips"]

    def get_last_metadata(self) -> Dict[str, Any]:
        """Returns the history of the last analysis run"""
        return {
            "attempts": self.history,
            "final_director": self.history[-1]["director"] if self.history else None
        }

    async def generate_edit_plan(
        self,
        video_paths: List[str],
        audio_track: Any,  # AudioTrack from schemas
        style: str,
        target_duration: float,
        job_id: Any
    ) -> Any:
        """
        Generate a complete EditPlan using AI analysis.
        
        This is the new "AI Editor Brain" method that:
        1. Analyzes beat map from audio
        2. Analyzes video clips for best moments
        3. Maps clips to beats based on style
        4. Selects appropriate transitions and effects
        5. Returns complete EditPlan ready for rendering or editing
        """
        from app.schemas.edit_plan import EditPlan, EditClip, Effect
        from app.services.style_editor import StyleEditor
        from app.services.ffmpeg_handler import FFmpegHandler
        from uuid import uuid4
        from datetime import datetime
        
        logger.info(f"Generating EditPlan for {len(video_paths)} videos, style={style}, duration={target_duration}s")
        
        style_editor = StyleEditor()
        ffmpeg = FFmpegHandler()
        
        # Get style configuration
        style_config = style_editor.get_style_config(style)
        ai_prompt_hint = style_config.get("ai_prompt", "") if style_config else ""
        
        # Get beats from audio track
        beats = audio_track.beats if hasattr(audio_track, 'beats') else []
        bpm = audio_track.bpm if hasattr(audio_track, 'bpm') else 120
        
        clips = []
        
        # Strategy: Try AI-powered cut selection first
        if self.gemini.model and video_paths:
            try:
                clips = await self._generate_clips_with_ai(
                    video_paths, beats, style, target_duration, ai_prompt_hint
                )
            except Exception as e:
                logger.warning(f"AI clip generation failed: {e}, falling back to beat-based")
        
        # Fallback: Beat-based automatic cutting
        if not clips:
            clips = self._generate_clips_from_beats(
                video_paths, beats, style, target_duration, ffmpeg
            )
        
        # Build the EditPlan
        plan = EditPlan(
            id=uuid4(),
            job_id=job_id,
            style=style,
            audio=audio_track,
            clips=clips,
            total_duration=target_duration,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            ai_model=self.gemini.model_name if self.gemini.model else "local_beat",
            generation_prompt=ai_prompt_hint[:500] if ai_prompt_hint else None,
            rendered=False
        )
        
        logger.info(f"EditPlan generated with {len(clips)} clips")
        return plan

    async def _generate_clips_with_ai(
        self,
        video_paths: List[str],
        beats: List[float],
        style: str,
        target_duration: float,
        ai_prompt_hint: str
    ) -> List[Any]:
        """Use Gemini to intelligently select and map clips to beats."""
        from app.schemas.edit_plan import EditClip, Effect
        from uuid import uuid4
        
        # Upload first video for analysis (or proxy)
        video_file = self.gemini.upload_to_gemini(video_paths[0])
        if not video_file:
            return []
        
        # Calculate optimal clip count based on style
        style_clip_lengths = {
            "cinematic_drama": (3, 6),    # Slower, longer cuts
            "energetic_dance": (1, 2.5),  # Fast, on-beat cuts
            "luxe_travel": (2.5, 5),      # Medium, smooth
            "modern_minimal": (2, 4),     # Clean, precise
            "viral_tiktok": (0.5, 2),     # Very fast, punchy
        }
        min_len, max_len = style_clip_lengths.get(style, (2, 4))
        estimated_clips = int(target_duration / ((min_len + max_len) / 2))
        
        # Get style-appropriate transitions and effects
        style_transitions = {
            "cinematic_drama": ["fade", "dissolve", "fadeblack"],
            "energetic_dance": ["fadewhite", "slideleft", "slideright", "circlecrop"],
            "luxe_travel": ["dissolve", "fade", "wipeleft"],
            "modern_minimal": ["fade", "dissolve"],
            "viral_tiktok": ["fadewhite", "pixelize", "slideleft", "circlecrop"],
        }
        style_effects = {
            "cinematic_drama": ["kenburns", "vignette", "slowmo"],
            "energetic_dance": ["zoomPunch", "shake", "colorPulse", "speedup"],
            "luxe_travel": ["kenburns", "vignette"],
            "modern_minimal": [],
            "viral_tiktok": ["zoomPunch", "flashWhite", "shake"],
        }
        
        transitions = style_transitions.get(style, ["fade"])
        effects = style_effects.get(style, [])
        
        prompt = f"""
        You are an expert video editor creating a {style} style reel.
        
        STYLE INSTRUCTIONS:
        {ai_prompt_hint}
        
        AUDIO INFO:
        - Target duration: {target_duration} seconds
        - Beat timestamps: {beats[:20]}... (showing first 20)
        - BPM: {len(beats) / target_duration * 60 if target_duration > 0 else 120:.0f}
        
        TASK:
        Watch this video and select {estimated_clips} clips that:
        1. Match the energy of "{style}" style
        2. Can be cut to land on the beat timestamps
        3. Each clip is {min_len}-{max_len} seconds long
        
        AVAILABLE TRANSITIONS: {transitions}
        AVAILABLE EFFECTS: {effects}
        
        Return ONLY a JSON list. Each clip must have:
        - start: start time in source video (seconds)
        - end: end time in source video (seconds)  
        - transition_in: one of {transitions}
        - effects: list of effect names from {effects} (can be empty)
        - reason: why this clip was chosen
        
        Example:
        [
            {{"start": 5.0, "end": 8.5, "transition_in": "fade", "effects": ["kenburns"], "reason": "Great establishing shot"}},
            {{"start": 22.0, "end": 24.5, "transition_in": "dissolve", "effects": [], "reason": "Action moment"}}
        ]
        """
        
        try:
            response = self.gemini.model.generate_content([video_file, prompt])
            text = response.text.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx]
            
            raw_clips = json.loads(text)
            
            # Convert to EditClip objects
            edit_clips = []
            timeline_pos = 0.0
            
            for i, clip_data in enumerate(raw_clips):
                clip_duration = clip_data["end"] - clip_data["start"]
                trans_dur = 0.5 if i > 0 else 0
                
                # Build effects list
                clip_effects = []
                for effect_name in clip_data.get("effects", []):
                    if effect_name in effects:
                        clip_effects.append(Effect(type=effect_name, params={}))
                
                edit_clip = EditClip(
                    id=f"clip-{i+1}",
                    source_video_id=None,
                    source_path=video_paths[0],  # TODO: support multiple sources
                    start_time=clip_data["start"],
                    end_time=clip_data["end"],
                    timeline_position=timeline_pos,
                    transition_in=clip_data.get("transition_in", "fade") if i > 0 else None,
                    transition_in_duration=trans_dur,
                    effects=clip_effects,
                    label=clip_data.get("reason", f"Clip {i+1}")
                )
                edit_clips.append(edit_clip)
                timeline_pos += clip_duration - trans_dur
            
            # Cleanup remote file
            try:
                genai.delete_file(video_file.name)
            except:
                pass
            
            return edit_clips
            
        except Exception as e:
            logger.error(f"AI clip generation parsing failed: {e}")
            try:
                genai.delete_file(video_file.name)
            except:
                pass
            return []

    def _generate_clips_from_beats(
        self,
        video_paths: List[str],
        beats: List[float],
        style: str,
        target_duration: float,
        ffmpeg: Any
    ) -> List[Any]:
        """Fallback: Generate clips by mapping beats to video segments."""
        from app.schemas.edit_plan import EditClip, Effect
        
        if not beats:
            # Generate evenly spaced "beats" if none provided
            interval = 2.0
            beats = [i * interval for i in range(int(target_duration / interval) + 1)]
        
        # Get video durations
        video_durations = []
        for vp in video_paths:
            info = ffmpeg.get_video_info(vp)
            video_durations.append((vp, info.get("duration", 30.0)))
        
        # Style-based clip length
        style_lengths = {
            "cinematic_drama": 4.0,
            "energetic_dance": 1.5,
            "luxe_travel": 3.5,
            "modern_minimal": 3.0,
            "viral_tiktok": 1.0,
        }
        base_length = style_lengths.get(style, 2.5)
        
        # Style-based transitions
        style_trans = {
            "cinematic_drama": "dissolve",
            "energetic_dance": "fadewhite",
            "luxe_travel": "fade",
            "modern_minimal": "fade",
            "viral_tiktok": "slideleft",
        }
        default_trans = style_trans.get(style, "fade")
        
        clips = []
        timeline_pos = 0.0
        beat_idx = 0
        video_idx = 0
        
        while timeline_pos < target_duration and beat_idx < len(beats) - 1:
            # Pick source video (round-robin)
            source_path, source_duration = video_durations[video_idx % len(video_durations)]
            
            # Calculate clip timing
            clip_start = (beat_idx * base_length) % max(source_duration - base_length, 1)
            clip_end = min(clip_start + base_length, source_duration)
            
            trans_dur = 0.5 if clips else 0
            
            clip = EditClip(
                id=f"clip-{len(clips)+1}",
                source_path=source_path,
                start_time=clip_start,
                end_time=clip_end,
                timeline_position=timeline_pos,
                transition_in=default_trans if clips else None,
                transition_in_duration=trans_dur,
                effects=[],
                label=f"Beat {beat_idx+1}"
            )
            clips.append(clip)
            
            timeline_pos += (clip_end - clip_start) - trans_dur
            beat_idx += 1
            video_idx += 1
        
        return clips
