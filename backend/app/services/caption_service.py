
import logging
import whisper
from pathlib import Path
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class CaptionService:
    """
    Service to generate AI Captions with word-level timestamps using OpenAI Whisper.
    """
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            # This might take a while on first run
            self._model = whisper.load_model(self.model_size)
        return self._model

    def generate_captions(self, audio_path: str, output_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio and generate word-level timestamps.
        Saves as a JSON for raw data and can later be used for ASS generation.
        """
        try:
            logger.info(f"Starting transcription for: {audio_path}")
            
            # Determine language - force English if very short to avoid hallucinations
            transcribe_options = {
                "word_timestamps": True,
                "verbose": False
            }
            
            # If the audio is extremely short, auto-detect often fails wildly (e.g. Malayalam)
            # For this project, we prioritize English stability.
            # You can remove 'language': 'en' if you want full multi-lang support later.
            transcribe_options["language"] = "en"
            
            result = self.model.transcribe(audio_path, **transcribe_options)
            detected_lang = result.get("language", "unknown")
            logger.info(f"Whisper processed with language: {detected_lang}")
            
            # Save raw JSON for debugging/future use
            json_path = Path(output_path).with_suffix(".json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return result.get("segments", [])

        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            raise

    def generate_ass_file(
        self, 
        segments: List[Dict[str, Any]], 
        output_path: str, 
        style: str = "classic",
        custom_colors: Dict[str, str] = None
    ):
        """
        Generate a styled .ass subtitle file for 'Opus-style' word-level highlighting.
        Supports styles: classic, tiktok, hormozi, neon.
        """
        from app.services.caption_styles import get_style
        
        style_config = get_style(style)
        
        # Override colors if provided
        if custom_colors:
            style_config = style_config.copy()
            style_config.update(custom_colors)
            
        # Build style string
        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        style_line = (
            f"Style: Default,"
            f"{style_config['font']},"
            f"{style_config['fontsize']},"
            f"{style_config['primary_color']},"
            f"{style_config['highlight_color'] if 'highlight_color' in style_config else '&H000000FF'}," # Secondary color (not used much in karaoke but good to have)
            f"{style_config['outline_color']},"
            f"{style_config['back_color']},"
            f"{style_config['bold']},"
            f"0,0,0,100,100,0,0,"
            f"{style_config['border_style']},"
            f"{style_config['outline']},"
            f"{style_config['shadow']},"
            f"{style_config['alignment']},"
            f"10,10,"
            f"{style_config['margin_v']},"
            f"1"
        )

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        events = []
        highlight_color = style_config.get("highlight_color", "&H0000FFFF")
        # Animation Handling
        # Standard Karaoke is {\k}. 
        # For 'pop', we might want per-word scaling, but ASS is limited. 
        # We'll stick to color highlighting for MVP as it's the most robust 'Opus' feature.
        
        for segment in segments:
            start_str = self._format_timestamp(segment["start"])
            end_str = self._format_timestamp(segment["end"])
            
            # To simulate highlighting, we use the words list
            if "words" in segment:
                word_text = ""
                for i, word_data in enumerate(segment["words"]):
                    # Standard ASS doesn't easily highlight words without complex scripting
                    # but we can use simple Karaoke-style timing \\k (which fills secondary color)
                    # OR we can explicitly color it if we want 'pop' effect.
                    # Karaoke {\k} uses SecondaryColour for "future" and Primary for "past" (or vice versa depending on player).
                    # Actually, standard behavior: Primary is "fill", Secondary is "karaoke fill".
                    # Let's use manual color tags for maximum compatibility: {\1c&H...}
                    
                    # BUT simpler: {\k<duration>} + standard styles.
                    # Let's check style definition. 
                    # If we want the "Active" word to be yellow, and others white:
                    # That's hard in one line without \\k.
                    # With \\k, the text changes from Secondary to Primary.
                    # So Secondary should be "Inactive" (White) and Primary "Active" (Yellow)?
                    # Usually it's the other way.
                    
                    # Implementation detail: We will stick to the standard OpenAI Whisper --> ASS logic 
                    # which highlights words as they are spoken. 
                    # The standard way is using {\k} or {\kf}.
                    
                    duration_cs = int((word_data["end"] - word_data["start"]) * 100)
                    
                    # If style has specific highlight color different from primary, we can inject color codes.
                    # But keeping it simple with just \\k for now, relying on SecondaryColour in style.
                    # Wait, our Style definition has Primary and Outline. Secondary is often ignored by non-karaoke renderers.
                    # FFmpeg's libass supports it.
                    
                    # Let's try explicit color highlighting for the 'Active' feel if requested?
                    # No, keep it robust: VSFilter compatible \\k.
                    
                    # Actually, better: Word-level animation is complex. 
                    # Let's just output the text with \\k tags which enables the color wipe.
                    
                    word_text += f"{{\\k{duration_cs}}}{word_data['word'].strip().upper()} "
                
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{word_text.strip()}")
            else:
                text = segment["text"].strip().upper()
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write("\n".join(events))

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to ASS timestamp format H:MM:SS.cs"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
