import google.generativeai as genai
import os
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class AIDirector:
    """
    AI Director service using Google Gemini 1.5 Pro to analyze video content
    and make editing decisions.
    """
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        else:
            logger.warning("Gemini API key not found. AI Director will not be available.")
            self.model = None

    def upload_to_gemini(self, video_path: str) -> Any:
        """Uploads a video file to Gemini File API."""
        if not self.model:
            return None
            
        logger.info(f"Uploading {video_path} to Gemini...")
        video_file = genai.upload_file(path=video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            logger.error("Video processing failed in Gemini.")
            return None
            
        logger.info(f"Video uploaded successfully: {video_file.uri}")
        return video_file

    def get_ai_cuts(self, video_paths: List[str], style: str, target_duration: float) -> List[Dict[str, float]]:
        """
        Asks Gemini to watch the videos and return a list of best segments.
        
        Returns:
            List of dicts: [{'source_index': 0, 'start': 10.5, 'end': 14.5}, ...]
        """
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
            genai.delete_file(video_file.name)
            
            return formatted_cuts

        except Exception as e:
            logger.error(f"Error in AI Director: {e}")
            return []
