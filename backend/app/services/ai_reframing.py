"""
AI-Powered Video Reframing Service
Combines YOLOv8 subject detection, SmolVLM frame analysis, and smart cropping
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SubjectBounds:
    """Bounding box for detected subject"""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_name: str
    
    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2
    
    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1

@dataclass
class FrameAnalysis:
    """Combined analysis result for a single frame"""
    frame_idx: int
    timestamp: float
    subjects: List[SubjectBounds]
    primary_subject: Optional[SubjectBounds]
    composition_score: float
    engagement_score: float
    crop_bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    needs_enhancement: bool

class AIReframingService:
    """Complete AI-powered video reframing with subject tracking"""
    
    def __init__(self):
        """Initialize all AI models"""
        self.yolo_available = False
        self.smol_vlm_available = False
        
        # Initialize YOLOv8
        try:
            from ultralytics import YOLO
            self.yolo_model = YOLO('yolov8n.pt')  # Lightweight model
            self.yolo_available = True
            logger.info("YOLOv8 initialized successfully")
        except Exception as e:
            logger.warning(f"YOLOv8 not available: {e}")
            self.yolo_model = None
        
        # Initialize SmolVLM (placeholder for now - can be replaced with actual model)
        try:
            # TODO: Replace with actual SmolVLM implementation
            self.smol_vlm_available = True
            logger.info("SmolVLM placeholder initialized")
        except Exception as e:
            logger.warning(f"SmolVLM not available: {e}")
        
        # Standard reel dimensions
        self.TARGET_WIDTH = 1080
        self.TARGET_HEIGHT = 1920
        self.TARGET_ASPECT = 9/16
    
    def analyze_video_for_reframing(
        self, 
        video_path: str,
        sample_rate: int = 10  # Analyze every 10th frame
    ) -> List[FrameAnalysis]:
        """
        Analyze entire video to determine optimal reframing strategy
        
        Args:
            video_path: Path to input video
            sample_rate: Analyze every Nth frame (higher = faster)
            
        Returns:
            List of frame analyses with optimal crop bounds
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            analyses = []
            frame_idx = 0
            
            logger.info(f"Analyzing video: {frame_count} frames at {fps} fps")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames for analysis
                if frame_idx % sample_rate == 0:
                    timestamp = frame_idx / fps
                    analysis = self._analyze_single_frame(frame, frame_idx, timestamp)
                    analyses.append(analysis)
                    
                    if frame_idx % (sample_rate * 30) == 0:  # Log every 30 sampled frames
                        logger.debug(f"Analyzed frame {frame_idx}/{frame_count}")
                
                frame_idx += 1
            
            cap.release()
            
            # Post-process analyses to smooth subject tracking
            analyses = self._smooth_subject_tracking(analyses)
            
            logger.info(f"Completed analysis: {len(analyses)} frames analyzed")
            return analyses
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return []
    
    def _analyze_single_frame(
        self, 
        frame: np.ndarray, 
        frame_idx: int, 
        timestamp: float
    ) -> FrameAnalysis:
        """Analyze a single frame for subjects and composition"""
        
        # Detect subjects with YOLOv8
        subjects = self._detect_subjects(frame)
        
        # Find primary subject (largest, most central person)
        primary_subject = self._find_primary_subject(subjects, frame.shape)
        
        # Calculate optimal crop bounds
        crop_bounds = self._calculate_optimal_crop(frame, primary_subject)
        
        # Analyze composition quality with SmolVLM
        composition_score = self._analyze_composition(frame, crop_bounds)
        engagement_score = self._analyze_engagement(frame, crop_bounds)
        
        # Check if enhancement needed
        needs_enhancement = self._needs_quality_enhancement(frame)
        
        return FrameAnalysis(
            frame_idx=frame_idx,
            timestamp=timestamp,
            subjects=subjects,
            primary_subject=primary_subject,
            composition_score=composition_score,
            engagement_score=engagement_score,
            crop_bounds=crop_bounds,
            needs_enhancement=needs_enhancement
        )
    
    def _detect_subjects(self, frame: np.ndarray) -> List[SubjectBounds]:
        """Detect people and other subjects in frame using YOLOv8"""
        subjects = []
        
        if not self.yolo_available:
            # Fallback: assume center crop
            h, w = frame.shape[:2]
            center_subject = SubjectBounds(
                x1=w*0.3, y1=h*0.2, x2=w*0.7, y2=h*0.8,
                confidence=0.5, class_name="person"
            )
            return [center_subject]
        
        try:
            # Run YOLOv8 detection
            results = self.yolo_model(frame, classes=[0])  # Class 0 = person
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        if confidence > 0.3:  # Minimum confidence threshold
                            subjects.append(SubjectBounds(
                                x1=float(x1), y1=float(y1),
                                x2=float(x2), y2=float(y2),
                                confidence=float(confidence),
                                class_name="person"
                            ))
            
            return subjects
            
        except Exception as e:
            logger.warning(f"YOLOv8 detection failed: {e}")
            return []
    
    def _find_primary_subject(
        self, 
        subjects: List[SubjectBounds], 
        frame_shape: Tuple[int, int, int]
    ) -> Optional[SubjectBounds]:
        """Find the most important subject to track"""
        if not subjects:
            return None
        
        h, w = frame_shape[:2]
        center_x, center_y = w / 2, h / 2
        
        # Score subjects by size and centrality
        scored_subjects = []
        for subject in subjects:
            # Size score (larger is better)
            area = subject.width * subject.height
            size_score = area / (w * h)
            
            # Centrality score (closer to center is better)
            dist_from_center = np.sqrt(
                (subject.center_x - center_x)**2 + 
                (subject.center_y - center_y)**2
            )
            max_distance = np.sqrt(center_x**2 + center_y**2)
            centrality_score = 1 - (dist_from_center / max_distance)
            
            # Combined score
            total_score = (
                size_score * 0.6 + 
                centrality_score * 0.3 + 
                subject.confidence * 0.1
            )
            
            scored_subjects.append((total_score, subject))
        
        # Return highest scoring subject
        scored_subjects.sort(key=lambda x: x[0], reverse=True)
        return scored_subjects[0][1]
    
    def _calculate_optimal_crop(
        self, 
        frame: np.ndarray, 
        primary_subject: Optional[SubjectBounds]
    ) -> Tuple[int, int, int, int]:
        """Calculate optimal crop bounds to 9:16 aspect ratio"""
        h, w = frame.shape[:2]
        
        # Target dimensions for 9:16 crop
        if w / h > self.TARGET_ASPECT:
            # Landscape video - crop width
            crop_height = h
            crop_width = int(h * self.TARGET_ASPECT)
            
            if primary_subject:
                # Center crop around primary subject
                subject_center_x = primary_subject.center_x
                crop_x1 = max(0, int(subject_center_x - crop_width / 2))
                crop_x1 = min(crop_x1, w - crop_width)
                crop_x2 = crop_x1 + crop_width
                
                # Add padding to keep subject fully in frame
                subject_padding = primary_subject.width * 0.2
                if crop_x1 > primary_subject.x1 - subject_padding:
                    crop_x1 = max(0, int(primary_subject.x1 - subject_padding))
                    crop_x2 = min(w, crop_x1 + crop_width)
                
                if crop_x2 < primary_subject.x2 + subject_padding:
                    crop_x2 = min(w, int(primary_subject.x2 + subject_padding))
                    crop_x1 = max(0, crop_x2 - crop_width)
            else:
                # Center crop if no subject detected
                crop_x1 = (w - crop_width) // 2
                crop_x2 = crop_x1 + crop_width
            
            crop_y1, crop_y2 = 0, h
            
        else:
            # Portrait or square video - crop height
            crop_width = w
            crop_height = int(w / self.TARGET_ASPECT)
            
            if primary_subject:
                # Center crop around primary subject
                subject_center_y = primary_subject.center_y
                crop_y1 = max(0, int(subject_center_y - crop_height / 2))
                crop_y1 = min(crop_y1, h - crop_height)
                crop_y2 = crop_y1 + crop_height
            else:
                # Center crop if no subject detected
                crop_y1 = (h - crop_height) // 2
                crop_y2 = crop_y1 + crop_height
            
            crop_x1, crop_x2 = 0, w
        
        return (crop_x1, crop_y1, crop_x2, crop_y2)
    
    def _analyze_composition(
        self, 
        frame: np.ndarray, 
        crop_bounds: Tuple[int, int, int, int]
    ) -> float:
        """Analyze composition quality using SmolVLM (placeholder implementation)"""
        if not self.smol_vlm_available:
            # Fallback: basic composition rules
            x1, y1, x2, y2 = crop_bounds
            cropped = frame[y1:y2, x1:x2]
            
            # Basic composition scoring
            score = 0.5  # Base score
            
            # Rule of thirds check
            h, w = cropped.shape[:2]
            thirds_x = [w//3, 2*w//3]
            thirds_y = [h//3, 2*h//3]
            
            # Check if there's content along rule of thirds lines (placeholder)
            score += 0.3
            
            return min(1.0, score)
        
        # TODO: Implement actual SmolVLM analysis
        try:
            x1, y1, x2, y2 = crop_bounds
            cropped = frame[y1:y2, x1:x2]
            
            # Placeholder SmolVLM prompt
            # score = self.smol_vlm.analyze(
            #     cropped,
            #     "Rate this video frame composition 0-1. Consider rule of thirds, subject placement, visual balance."
            # )
            
            # For now, return placeholder score
            return 0.7
            
        except Exception as e:
            logger.warning(f"SmolVLM composition analysis failed: {e}")
            return 0.5
    
    def _analyze_engagement(
        self, 
        frame: np.ndarray, 
        crop_bounds: Tuple[int, int, int, int]
    ) -> float:
        """Analyze frame engagement potential using SmolVLM"""
        if not self.smol_vlm_available:
            # Fallback: basic engagement heuristics
            x1, y1, x2, y2 = crop_bounds
            cropped = frame[y1:y2, x1:x2]
            
            # Basic engagement scoring
            score = 0.5
            
            # Check brightness/contrast
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            contrast = gray.std()
            brightness = gray.mean()
            
            if 50 < brightness < 200 and contrast > 30:
                score += 0.2
            
            return min(1.0, score)
        
        # TODO: Implement actual SmolVLM engagement analysis
        try:
            x1, y1, x2, y2 = crop_bounds
            cropped = frame[y1:y2, x1:x2]
            
            # Placeholder SmolVLM prompt
            # score = self.smol_vlm.analyze(
            #     cropped,
            #     "Rate this frame 0-1 for social media engagement. Consider: facial expressions, actions, visual interest."
            # )
            
            return 0.6  # Placeholder
            
        except Exception as e:
            logger.warning(f"SmolVLM engagement analysis failed: {e}")
            return 0.5
    
    def _needs_quality_enhancement(self, frame: np.ndarray) -> bool:
        """Determine if frame needs quality enhancement"""
        h, w = frame.shape[:2]
        
        # Check if resolution is below target
        if w < self.TARGET_WIDTH or h < self.TARGET_HEIGHT:
            return True
        
        # Check if image is blurry (basic laplacian variance)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        return variance < 100  # Threshold for blur detection
    
    def _smooth_subject_tracking(
        self, 
        analyses: List[FrameAnalysis]
    ) -> List[FrameAnalysis]:
        """Smooth subject tracking to avoid jittery crops"""
        if len(analyses) < 3:
            return analyses
        
        # Simple moving average smoothing for crop bounds
        window_size = 3
        smoothed_analyses = []
        
        for i, analysis in enumerate(analyses):
            if i < window_size // 2 or i >= len(analyses) - window_size // 2:
                smoothed_analyses.append(analysis)
                continue
            
            # Calculate average crop bounds in window
            window_analyses = analyses[i - window_size//2:i + window_size//2 + 1]
            
            avg_x1 = sum(a.crop_bounds[0] for a in window_analyses) / len(window_analyses)
            avg_y1 = sum(a.crop_bounds[1] for a in window_analyses) / len(window_analyses)
            avg_x2 = sum(a.crop_bounds[2] for a in window_analyses) / len(window_analyses)
            avg_y2 = sum(a.crop_bounds[3] for a in window_analyses) / len(window_analyses)
            
            # Create smoothed analysis
            smoothed_analysis = FrameAnalysis(
                frame_idx=analysis.frame_idx,
                timestamp=analysis.timestamp,
                subjects=analysis.subjects,
                primary_subject=analysis.primary_subject,
                composition_score=analysis.composition_score,
                engagement_score=analysis.engagement_score,
                crop_bounds=(int(avg_x1), int(avg_y1), int(avg_x2), int(avg_y2)),
                needs_enhancement=analysis.needs_enhancement
            )
            
            smoothed_analyses.append(smoothed_analysis)
        
        return smoothed_analyses
    
    def apply_smart_reframing(
        self,
        input_video_path: str,
        output_video_path: str,
        analyses: Optional[List[FrameAnalysis]] = None
    ) -> bool:
        """
        Apply smart reframing to video based on analysis
        
        Args:
            input_video_path: Path to input video
            output_video_path: Path for output video
            analyses: Pre-computed analyses (optional)
            
        Returns:
            Success status
        """
        try:
            if analyses is None:
                logger.info("Analyzing video for reframing...")
                analyses = self.analyze_video_for_reframing(input_video_path)
            
            if not analyses:
                logger.error("No analysis data available for reframing")
                return False
            
            logger.info(f"Applying reframing with {len(analyses)} analysis points")
            
            # Get most common crop bounds (for consistency)
            crop_bounds = self._get_optimal_crop_bounds(analyses)
            
            # Apply crop using FFmpeg
            success = self._apply_ffmpeg_crop(
                input_video_path,
                output_video_path,
                crop_bounds
            )
            
            if success:
                logger.info(f"Smart reframing completed: {output_video_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying smart reframing: {e}")
            return False
    
    def _get_optimal_crop_bounds(
        self, 
        analyses: List[FrameAnalysis]
    ) -> Tuple[int, int, int, int]:
        """Get optimal crop bounds based on all analyses"""
        
        # Weight by engagement and composition scores
        weighted_bounds = []
        total_weight = 0
        
        for analysis in analyses:
            weight = (analysis.engagement_score + analysis.composition_score) / 2
            weighted_bounds.append((analysis.crop_bounds, weight))
            total_weight += weight
        
        if total_weight == 0:
            # Fallback to first analysis
            return analyses[0].crop_bounds
        
        # Calculate weighted average
        avg_x1 = sum(bounds[0] * weight for bounds, weight in weighted_bounds) / total_weight
        avg_y1 = sum(bounds[1] * weight for bounds, weight in weighted_bounds) / total_weight
        avg_x2 = sum(bounds[2] * weight for bounds, weight in weighted_bounds) / total_weight
        avg_y2 = sum(bounds[3] * weight for bounds, weight in weighted_bounds) / total_weight
        
        return (int(avg_x1), int(avg_y1), int(avg_x2), int(avg_y2))
    
    def _apply_ffmpeg_crop(
        self,
        input_path: str,
        output_path: str,
        crop_bounds: Tuple[int, int, int, int]
    ) -> bool:
        """Apply crop and resize using FFmpeg"""
        try:
            x1, y1, x2, y2 = crop_bounds
            crop_width = x2 - x1
            crop_height = y2 - y1
            
            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-filter_complex",
                f"crop={crop_width}:{crop_height}:{x1}:{y1},scale={self.TARGET_WIDTH}:{self.TARGET_HEIGHT}",
                "-c:a", "copy",
                "-preset", "fast",
                output_path
            ]
            
            logger.debug(f"FFmpeg crop command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg crop failed: {result.stderr}")
                return False
            
            # Verify output exists
            if not Path(output_path).exists():
                logger.error(f"Output file not created: {output_path}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg crop operation timed out")
            return False
        except Exception as e:
            logger.error(f"Error applying FFmpeg crop: {e}")
            return False
    
    def get_reframing_stats(self, analyses: List[FrameAnalysis]) -> Dict:
        """Get statistics about the reframing analysis"""
        if not analyses:
            return {}
        
        total_frames = len(analyses)
        avg_engagement = sum(a.engagement_score for a in analyses) / total_frames
        avg_composition = sum(a.composition_score for a in analyses) / total_frames
        
        subjects_detected = sum(1 for a in analyses if a.primary_subject is not None)
        enhancement_needed = sum(1 for a in analyses if a.needs_enhancement)
        
        return {
            "total_frames_analyzed": total_frames,
            "average_engagement_score": round(avg_engagement, 3),
            "average_composition_score": round(avg_composition, 3),
            "frames_with_subjects": subjects_detected,
            "subject_detection_rate": round(subjects_detected / total_frames, 3),
            "frames_needing_enhancement": enhancement_needed,
            "enhancement_rate": round(enhancement_needed / total_frames, 3)
        }