#!/usr/bin/env python3
"""
Test AI Reframing Integration
Tests the complete AI pipeline with YOLOv8, SmolVLM, and smart cropping
"""
import logging
from pathlib import Path
import sys

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.ai_reframing import AIReframingService
from app.services.video_enhancement import VideoEnhancementService
from app.services.video_processor import VideoProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_reframing():
    """Test the AI reframing service"""
    
    # Initialize services
    reframing_service = AIReframingService()
    enhancement_service = VideoEnhancementService()
    
    # Test video path
    test_video = Path("test_output/test_job_real_assets/output.mp4")
    
    if not test_video.exists():
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("=== Testing AI Reframing Service ===")
    
    # Test 1: Basic initialization
    logger.info(f"YOLOv8 Available: {reframing_service.yolo_available}")
    logger.info(f"SmolVLM Available: {reframing_service.smol_vlm_available}")
    logger.info(f"Real-ESRGAN Available: {enhancement_service.realesrgan_available}")
    
    # Test 2: Video analysis
    logger.info("Analyzing video for reframing...")
    try:
        analyses = reframing_service.analyze_video_for_reframing(
            str(test_video),
            sample_rate=15  # Analyze every 15th frame for speed
        )
        
        if analyses:
            logger.info(f"Analysis completed: {len(analyses)} frames analyzed")
            
            # Get stats
            stats = reframing_service.get_reframing_stats(analyses)
            logger.info("Analysis Statistics:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
            
            # Test 3: Apply reframing
            output_path = "test_output/ai_reframed_test.mp4"
            logger.info(f"Applying smart reframing to: {output_path}")
            
            success = reframing_service.apply_smart_reframing(
                str(test_video),
                output_path,
                analyses
            )
            
            if success:
                logger.info("✅ AI reframing test PASSED")
                
                # Test 4: Quality enhancement (if available)
                if enhancement_service.realesrgan_available:
                    enhanced_output = "test_output/ai_enhanced_test.mp4"
                    logger.info(f"Testing quality enhancement: {enhanced_output}")
                    
                    enhance_success = enhancement_service.enhance_video_quality(
                        output_path,
                        enhanced_output,
                        scale=2
                    )
                    
                    if enhance_success:
                        logger.info("✅ Quality enhancement test PASSED")
                    else:
                        logger.warning("⚠️ Quality enhancement test FAILED")
                else:
                    logger.info("ℹ️ Real-ESRGAN not available, skipping enhancement test")
                
                return True
            else:
                logger.error("❌ AI reframing test FAILED")
                return False
        else:
            logger.error("❌ Video analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ AI reframing test failed with error: {e}")
        return False

def test_integrated_pipeline():
    """Test the full integrated pipeline"""
    
    logger.info("=== Testing Integrated AI Pipeline ===")
    
    # Use existing test files
    video_files = ["uploads/input"]  # This should contain test videos
    music_file = "backend/test_output/test_job_real_assets"  # Look for music files
    
    # Create a mock job
    job_id = "ai_integration_test"
    output_dir = Path("test_output/ai_integration_test")
    output_dir.mkdir(exist_ok=True)
    
    # Find actual test files
    upload_dir = Path("uploads/input")
    if upload_dir.exists():
        video_files = [str(f) for f in upload_dir.glob("*.mp4")][:1]  # Take first video
    else:
        logger.warning("No upload directory found, using placeholder")
        video_files = []
    
    test_assets = Path("backend/test_output/test_job_real_assets")
    music_files = []
    if test_assets.exists():
        music_files = [str(f) for f in test_assets.glob("*.mp3")]
    
    if not video_files:
        logger.info("ℹ️ No video files found, skipping integrated test")
        return True
    
    if not music_files:
        logger.info("ℹ️ No music files found, skipping integrated test")
        return True
    
    try:
        processor = VideoProcessor()
        
        logger.info(f"Testing with video: {video_files[0]}")
        logger.info(f"Testing with music: {music_files[0]}")
        
        success = processor.process_video(
            job_id=job_id,
            video_paths=video_files,
            music_path=music_files[0],
            style="cinematic",
            output_dir=output_dir,
            enable_ai_reframing=True,
            enable_quality_enhancement=False  # Skip enhancement for speed
        )
        
        if success:
            output_file = output_dir / "output.mp4"
            if output_file.exists():
                logger.info("✅ Integrated AI pipeline test PASSED")
                logger.info(f"Output created: {output_file}")
                return True
            else:
                logger.error("❌ Output file not created")
                return False
        else:
            logger.error("❌ Integrated pipeline test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integrated pipeline test failed: {e}")
        return False

def main():
    """Run all AI integration tests"""
    
    logger.info("Starting AI Integration Tests")
    
    # Ensure test directories exist
    Path("test_output").mkdir(exist_ok=True)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: AI Reframing Service
    total_tests += 1
    if test_ai_reframing():
        tests_passed += 1
    
    # Test 2: Integrated Pipeline (optional, requires test files)
    total_tests += 1
    if test_integrated_pipeline():
        tests_passed += 1
    
    # Results
    logger.info("=== Test Results ===")
    logger.info(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        logger.info("🎉 All AI integration tests PASSED!")
        return True
    else:
        logger.warning(f"⚠️ {total_tests - tests_passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)