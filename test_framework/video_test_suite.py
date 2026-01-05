#!/usr/bin/env python3
"""
AI Video Reframing Test Suite
Comprehensive testing framework for landscape conversion, subject tracking, transitions, and reframing
"""
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import cv2
import numpy as np
import sys

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.ai_reframing import AIReframingService
from app.services.video_enhancement import VideoEnhancementService
from app.services.video_processor import VideoProcessor
from app.services.ffmpeg_handler import FFmpegHandler

logger = logging.getLogger(__name__)

class TestType(Enum):
    """Types of tests available"""
    LANDSCAPE_CONVERSION = "landscape_conversion"
    SUBJECT_TRACKING = "subject_tracking"
    TRANSITION_EFFECTS = "transition_effects"
    REALTIME_REFRAMING = "realtime_reframing"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    FULL_PIPELINE = "full_pipeline"

class VideoType(Enum):
    """Types of input videos"""
    STATIC_LANDSCAPE = "static_landscape"  # No moving subjects
    MOVING_SUBJECT = "moving_subject"     # People/objects moving
    MULTIPLE_SUBJECTS = "multiple_subjects" # Multiple people
    TALKING_HEAD = "talking_head"         # Single person speaking
    ACTION_SCENE = "action_scene"         # Fast movement/sports
    NATURE_SCENE = "nature_scene"         # Landscapes/scenery

@dataclass
class TestVideo:
    """Test video metadata"""
    name: str
    path: str
    video_type: VideoType
    width: int
    height: int
    duration: float
    fps: float
    description: str
    expected_subjects: int = 0
    has_motion: bool = False
    quality_level: str = "medium"  # low, medium, high

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_type: TestType
    input_video: str
    output_video: str
    success: bool
    duration: float
    metrics: Dict[str, Any]
    errors: List[str]
    timestamp: str

@dataclass
class TestSuiteResults:
    """Complete test suite results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration: float
    results: List[TestResult]
    summary: Dict[str, Any]

class VideoTestSuite:
    """Comprehensive AI Video Reframing Test Suite"""
    
    def __init__(self, test_dir: str = "test_framework/test_videos"):
        """Initialize test suite"""
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = Path("test_framework/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI services
        self.ai_reframing = AIReframingService()
        self.video_enhancer = VideoEnhancementService()
        self.video_processor = VideoProcessor()
        self.ffmpeg = FFmpegHandler()
        
        # Test video registry
        self.test_videos: List[TestVideo] = []
        
        # Load existing test videos
        self._load_test_videos()
    
    def _load_test_videos(self):
        """Load test videos from directory and registry"""
        registry_file = self.test_dir / "video_registry.json"
        
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)
                    for video_data in data.get("videos", []):
                        video_data["video_type"] = VideoType(video_data["video_type"])
                        self.test_videos.append(TestVideo(**video_data))
                logger.info(f"Loaded {len(self.test_videos)} test videos from registry")
            except Exception as e:
                logger.warning(f"Failed to load video registry: {e}")
        
        # Auto-discover videos in test directory
        self._discover_videos()
    
    def _discover_videos(self):
        """Automatically discover video files in test directory"""
        video_extensions = {".mp4", ".avi", ".mov", ".mkv"}
        existing_paths = {v.path for v in self.test_videos}
        
        for video_file in self.test_dir.rglob("*"):
            if video_file.suffix.lower() in video_extensions and str(video_file) not in existing_paths:
                try:
                    # Get video info
                    info = self.ffmpeg.get_video_info(str(video_file))
                    if info:
                        # Determine video type based on filename and properties
                        video_type = self._classify_video_type(video_file.name, info)
                        
                        test_video = TestVideo(
                            name=video_file.stem,
                            path=str(video_file),
                            video_type=video_type,
                            width=info.get("width", 0),
                            height=info.get("height", 0),
                            duration=info.get("duration", 0),
                            fps=info.get("fps", 30),
                            description=f"Auto-discovered {video_type.value} video",
                            has_motion=True  # Assume motion for auto-discovered videos
                        )
                        
                        self.test_videos.append(test_video)
                        logger.info(f"Discovered test video: {video_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to analyze video {video_file}: {e}")
    
    def _classify_video_type(self, filename: str, info: Dict) -> VideoType:
        """Classify video type based on filename and properties"""
        filename_lower = filename.lower()
        width = info.get("width", 0)
        height = info.get("height", 0)
        
        # Check aspect ratio
        if width > height * 1.5:  # Landscape
            if "nature" in filename_lower or "landscape" in filename_lower:
                return VideoType.NATURE_SCENE
            elif "action" in filename_lower or "sport" in filename_lower:
                return VideoType.ACTION_SCENE
            elif "talk" in filename_lower or "head" in filename_lower:
                return VideoType.TALKING_HEAD
            else:
                return VideoType.STATIC_LANDSCAPE
        else:
            return VideoType.MOVING_SUBJECT
    
    def add_test_video(
        self,
        video_path: str,
        video_type: VideoType,
        name: Optional[str] = None,
        description: str = "",
        expected_subjects: int = 0,
        has_motion: bool = False,
        quality_level: str = "medium"
    ) -> TestVideo:
        """Add a new test video to the suite"""
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get video info
        info = self.ffmpeg.get_video_info(str(video_path))
        if not info:
            raise ValueError(f"Could not analyze video: {video_path}")
        
        test_video = TestVideo(
            name=name or video_path.stem,
            path=str(video_path),
            video_type=video_type,
            width=info.get("width", 0),
            height=info.get("height", 0),
            duration=info.get("duration", 0),
            fps=info.get("fps", 30),
            description=description,
            expected_subjects=expected_subjects,
            has_motion=has_motion,
            quality_level=quality_level
        )
        
        self.test_videos.append(test_video)
        self._save_video_registry()
        
        logger.info(f"Added test video: {test_video.name} ({video_type.value})")
        return test_video
    
    def _save_video_registry(self):
        """Save video registry to file"""
        registry_file = self.test_dir / "video_registry.json"
        
        registry_data = {
            "videos": [
                {
                    **asdict(video),
                    "video_type": video.video_type.value
                }
                for video in self.test_videos
            ]
        }
        
        try:
            with open(registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save video registry: {e}")
    
    def create_test_videos(self):
        """Create synthetic test videos for different scenarios"""
        logger.info("Creating synthetic test videos for comprehensive testing")
        
        test_scenarios = [
            {
                "name": "static_landscape_1920x1080",
                "size": (1920, 1080),
                "type": VideoType.STATIC_LANDSCAPE,
                "duration": 5,
                "description": "Static landscape with geometric shapes"
            },
            {
                "name": "moving_subject_landscape",
                "size": (1920, 1080),
                "type": VideoType.MOVING_SUBJECT,
                "duration": 8,
                "description": "Landscape with moving rectangular subject"
            },
            {
                "name": "multiple_subjects_wide",
                "size": (1920, 1080),
                "type": VideoType.MULTIPLE_SUBJECTS,
                "duration": 6,
                "description": "Multiple moving subjects in wide frame"
            },
            {
                "name": "talking_head_landscape",
                "size": (1920, 1080),
                "type": VideoType.TALKING_HEAD,
                "duration": 10,
                "description": "Simulated talking head in landscape format"
            }
        ]
        
        for scenario in test_scenarios:
            video_path = self.test_dir / f"{scenario['name']}.mp4"
            
            if not video_path.exists():
                self._create_synthetic_video(
                    str(video_path),
                    scenario['size'],
                    scenario['duration'],
                    scenario['type']
                )
                
                self.add_test_video(
                    str(video_path),
                    scenario['type'],
                    scenario['name'],
                    scenario['description'],
                    expected_subjects=1 if 'subject' in scenario['name'] else 0,
                    has_motion='moving' in scenario['name']
                )
    
    def _create_synthetic_video(
        self,
        output_path: str,
        size: Tuple[int, int],
        duration: int,
        video_type: VideoType
    ):
        """Create synthetic test video"""
        width, height = size
        fps = 30
        total_frames = duration * fps
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, size)
        
        try:
            for frame_num in range(total_frames):
                frame = self._generate_test_frame(
                    frame_num, total_frames, size, video_type
                )
                out.write(frame)
            
            logger.info(f"Created synthetic video: {output_path}")
            
        finally:
            out.release()
    
    def _generate_test_frame(
        self,
        frame_num: int,
        total_frames: int,
        size: Tuple[int, int],
        video_type: VideoType
    ) -> np.ndarray:
        """Generate a single test frame"""
        width, height = size
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Base background gradient
        progress = frame_num / total_frames
        bg_color = int(50 + 100 * np.sin(progress * np.pi * 2))
        frame[:, :] = [bg_color, 80, 120]
        
        if video_type == VideoType.STATIC_LANDSCAPE:
            # Static geometric shapes
            cv2.rectangle(frame, (width//4, height//4), (3*width//4, 3*height//4), (255, 255, 255), 2)
            cv2.circle(frame, (width//2, height//2), min(width, height)//8, (255, 255, 0), -1)
            
        elif video_type == VideoType.MOVING_SUBJECT:
            # Moving subject (simulated person)
            subject_x = int(width * 0.3 + (width * 0.4) * np.sin(progress * np.pi * 4))
            subject_y = int(height * 0.2 + (height * 0.6) * progress)
            
            # Draw "person" rectangle
            cv2.rectangle(
                frame,
                (subject_x - 50, subject_y - 100),
                (subject_x + 50, subject_y + 100),
                (255, 255, 255),
                -1
            )
            
            # Add "head"
            cv2.circle(frame, (subject_x, subject_y - 120), 30, (255, 200, 200), -1)
            
        elif video_type == VideoType.MULTIPLE_SUBJECTS:
            # Multiple moving subjects
            for i in range(3):
                offset = i * 2 * np.pi / 3
                subject_x = int(width * 0.5 + width * 0.3 * np.cos(progress * np.pi * 2 + offset))
                subject_y = int(height * 0.5 + height * 0.3 * np.sin(progress * np.pi * 2 + offset))
                
                color = [(255, 100, 100), (100, 255, 100), (100, 100, 255)][i]
                cv2.rectangle(
                    frame,
                    (subject_x - 30, subject_y - 60),
                    (subject_x + 30, subject_y + 60),
                    color,
                    -1
                )
        
        elif video_type == VideoType.TALKING_HEAD:
            # Stationary talking head with slight movement
            head_x = int(width * 0.5 + 20 * np.sin(progress * np.pi * 8))  # Slight head movement
            head_y = int(height * 0.4)
            
            # Draw "person" body
            cv2.rectangle(
                frame,
                (head_x - 80, head_y),
                (head_x + 80, head_y + 200),
                (200, 180, 160),
                -1
            )
            
            # Draw "head"
            cv2.circle(frame, (head_x, head_y - 50), 60, (255, 220, 200), -1)
            
            # Simulate "talking" with changing mouth
            mouth_open = int(10 * abs(np.sin(progress * np.pi * 20))) + 5
            cv2.ellipse(
                frame,
                (head_x, head_y - 30),
                (15, mouth_open),
                0, 0, 360,
                (100, 50, 50),
                -1
            )
        
        # Add frame counter and info
        cv2.putText(
            frame,
            f"Frame {frame_num}/{total_frames}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        cv2.putText(
            frame,
            f"{video_type.value.upper()}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )
        
        return frame