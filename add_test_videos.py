#!/usr/bin/env python3
"""
AI Video Test Framework - Video Manager
Add external videos to the test framework
"""
import logging
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from test_framework.video_test_suite import VideoTestSuite, VideoType

logger = logging.getLogger(__name__)

class VideoManager:
    """Manage test videos for the AI reframing test framework"""
    
    def __init__(self):
        self.test_suite = VideoTestSuite()
    
    def add_existing_videos(self):
        """Add existing videos from uploads directory"""
        uploads_dir = Path("backend/uploads/input")
        
        if not uploads_dir.exists():
            logger.warning(f"Uploads directory not found: {uploads_dir}")
            return
        
        video_files = list(uploads_dir.glob("*.mp4"))
        
        for video_file in video_files:
            try:
                # Classify the video based on filename
                filename = video_file.name.lower()
                
                if "arunachal" in filename or "nature" in filename or "hills" in filename:
                    video_type = VideoType.NATURE_SCENE
                elif "menchukha" in filename or "village" in filename:
                    video_type = VideoType.STATIC_LANDSCAPE
                else:
                    video_type = VideoType.MOVING_SUBJECT
                
                # Add to test suite
                test_video = self.test_suite.add_test_video(
                    video_path=str(video_file),
                    video_type=video_type,
                    name=video_file.stem,
                    description=f"Real content from uploads: {video_file.name}",
                    expected_subjects=1 if "subject" in video_type.value else 0,
                    has_motion=True,
                    quality_level="medium"
                )
                
                logger.info(f"✅ Added: {test_video.name} ({video_type.value})")
                logger.info(f"   Dimensions: {test_video.width}x{test_video.height}")
                logger.info(f"   Duration: {test_video.duration:.1f}s")
                
            except Exception as e:
                logger.error(f"❌ Failed to add {video_file}: {e}")
    
    def list_test_videos(self):
        """List all available test videos"""
        logger.info("📹 Available Test Videos:")
        logger.info("="*60)
        
        for i, video in enumerate(self.test_suite.test_videos, 1):
            aspect_ratio = video.width / video.height if video.height > 0 else 0
            is_landscape = "📺 Landscape" if aspect_ratio > 1.3 else "📱 Portrait" if aspect_ratio < 0.8 else "⬜ Square"
            
            logger.info(f"{i:2d}. {video.name}")
            logger.info(f"    Type: {video.video_type.value}")
            logger.info(f"    Format: {is_landscape} ({video.width}x{video.height}, {aspect_ratio:.2f})")
            logger.info(f"    Duration: {video.duration:.1f}s @ {video.fps} fps")
            logger.info(f"    Path: {video.path}")
            logger.info("")

def main():
    """Main video manager entry point"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    manager = VideoManager()
    
    print("🎬 AI Video Test Framework - Video Manager")
    print("=" * 50)
    
    # Add existing videos from uploads
    print("📂 Adding existing videos from uploads...")
    manager.add_existing_videos()
    
    print(f"\\n📊 Total test videos: {len(manager.test_suite.test_videos)}")
    
    # List all videos
    print("\\n")
    manager.list_test_videos()
    
    print("✅ Video management complete!")
    print("\\nNext steps:")
    print("  1. Run tests: python test_framework/main.py --test-type all")
    print("  2. Run specific tests: python test_framework/main.py --test-type landscape")
    print("  3. Filter by video: python test_framework/main.py --video-filter arunachal")

if __name__ == "__main__":
    main()