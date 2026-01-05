#!/usr/bin/env python3
"""
Simple AI Reframing Test Interface
Easy testing: paste videos, select tests, get results
"""
import logging
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import sys

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.ai_reframing import AIReframingService
from app.services.video_processor import VideoProcessor
from app.services.ffmpeg_handler import FFmpegHandler

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SimpleTestRunner:
    """Simple test runner for AI reframing"""
    
    def __init__(self):
        """Initialize test runner"""
        # Create directory structure
        self.setup_directories()
        
        # Initialize AI services
        self.ai_reframing = AIReframingService()
        self.video_processor = VideoProcessor()
        self.ffmpeg = FFmpegHandler()
    
    def setup_directories(self):
        """Set up directory structure"""
        self.base_dir = Path("easy_test")
        self.input_dir = self.base_dir / "input_videos"
        self.output_dir = self.base_dir / "output_results"
        self.temp_dir = self.base_dir / "temp"
        
        # Create directories
        for dir_path in [self.input_dir, self.output_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create README for input directory
        readme_content = """
# Input Videos Directory

## How to Use:
1. **Paste your video files here** (MP4, AVI, MOV supported)
2. **Run tests**: `python easy_test_runner.py`
3. **Check results**: Look in `output_results` folder

## Supported Video Types:
- **Landscape videos** (16:9, 1920x1080, etc.) - Will be converted to 9:16 portrait
- **Any resolution** - AI will analyze and reframe
- **Any duration** - Works with short clips or longer videos

## Available Test Cases:
- **landscape_conversion** - Convert landscape → portrait (9:16)
- **subject_tracking** - Detect and track people/objects
- **realtime_reframing** - Fast processing for real-time use
- **full_pipeline** - Complete video processing with music

## Results:
- Each test creates output videos in `output_results/`
- Test reports saved as JSON files
- Side-by-side comparisons available
"""
        
        readme_file = self.input_dir / "README.md"
        if not readme_file.exists():
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
    
    def discover_input_videos(self) -> List[Path]:
        """Find all video files in input directory"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.m4v'}
        
        videos = []
        for ext in video_extensions:
            videos.extend(self.input_dir.glob(f"*{ext}"))
            videos.extend(self.input_dir.glob(f"*{ext.upper()}"))
        
        return sorted(videos)
    
    def analyze_video(self, video_path: Path) -> Dict:
        """Quick video analysis"""
        try:
            info = self.ffmpeg.get_video_info(str(video_path))
            if not info:
                return {"error": "Could not analyze video"}
            
            width = info.get('width', 0)
            height = info.get('height', 0)
            duration = info.get('duration', 0)
            
            # Determine video characteristics
            aspect_ratio = width / height if height > 0 else 0
            if aspect_ratio > 1.5:
                format_type = "Landscape"
                suitable_for = ["landscape_conversion", "subject_tracking", "realtime_reframing"]
            elif aspect_ratio < 0.7:
                format_type = "Portrait"
                suitable_for = ["subject_tracking", "realtime_reframing"]
            else:
                format_type = "Square"
                suitable_for = ["subject_tracking", "realtime_reframing"]
            
            return {
                "width": width,
                "height": height,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "format_type": format_type,
                "suitable_tests": suitable_for,
                "file_size_mb": video_path.stat().st_size / (1024 * 1024)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_landscape_conversion(self, video_path: Path, output_name: str) -> Dict:
        """Run landscape → portrait conversion test"""
        logger.info(f"🔄 Running landscape conversion: {video_path.name}")
        
        output_path = self.output_dir / f"{output_name}_landscape_converted.mp4"
        
        try:
            # Analyze video for reframing
            analyses = self.ai_reframing.analyze_video_for_reframing(
                str(video_path), sample_rate=8
            )
            
            if not analyses:
                return {"success": False, "error": "Video analysis failed"}
            
            # Get stats
            stats = self.ai_reframing.get_reframing_stats(analyses)
            
            # Apply reframing
            success = self.ai_reframing.apply_smart_reframing(
                str(video_path), str(output_path), analyses
            )
            
            if success:
                # Verify output
                output_info = self.ffmpeg.get_video_info(str(output_path))
                return {
                    "success": True,
                    "output_file": str(output_path),
                    "stats": stats,
                    "output_dimensions": f"{output_info.get('width', 0)}x{output_info.get('height', 0)}" if output_info else "Unknown"
                }
            else:
                return {"success": False, "error": "Reframing failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_subject_tracking(self, video_path: Path, output_name: str) -> Dict:
        """Run subject detection and tracking test"""
        logger.info(f"👁️ Running subject tracking: {video_path.name}")
        
        output_path = self.output_dir / f"{output_name}_subject_tracked.mp4"
        
        try:
            # Detailed analysis for subject tracking
            analyses = self.ai_reframing.analyze_video_for_reframing(
                str(video_path), sample_rate=5  # More frequent sampling
            )
            
            if not analyses:
                return {"success": False, "error": "Subject analysis failed"}
            
            # Count subjects detected
            frames_with_subjects = sum(1 for a in analyses if a.primary_subject is not None)
            detection_rate = frames_with_subjects / len(analyses) if analyses else 0
            
            # Apply subject-aware reframing
            success = self.ai_reframing.apply_smart_reframing(
                str(video_path), str(output_path), analyses
            )
            
            if success:
                return {
                    "success": True,
                    "output_file": str(output_path),
                    "detection_rate": f"{detection_rate:.1%}",
                    "frames_analyzed": len(analyses),
                    "frames_with_subjects": frames_with_subjects
                }
            else:
                return {"success": False, "error": "Subject tracking reframing failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_realtime_reframing(self, video_path: Path, output_name: str) -> Dict:
        """Run real-time processing speed test"""
        logger.info(f"⚡ Running real-time reframing: {video_path.name}")
        
        output_path = self.output_dir / f"{output_name}_realtime.mp4"
        
        try:
            import time
            start_time = time.time()
            
            # Fast analysis for real-time
            analyses = self.ai_reframing.analyze_video_for_reframing(
                str(video_path), sample_rate=10  # Faster sampling
            )
            
            analysis_time = time.time() - start_time
            
            if not analyses:
                return {"success": False, "error": "Real-time analysis failed"}
            
            # Apply reframing
            reframe_start = time.time()
            success = self.ai_reframing.apply_smart_reframing(
                str(video_path), str(output_path), analyses
            )
            reframe_time = time.time() - reframe_start
            
            # Get video duration
            video_info = self.ffmpeg.get_video_info(str(video_path))
            video_duration = video_info.get('duration', 0) if video_info else 0
            
            total_time = analysis_time + reframe_time
            speed_ratio = total_time / video_duration if video_duration > 0 else float('inf')
            
            if success:
                return {
                    "success": True,
                    "output_file": str(output_path),
                    "analysis_time": f"{analysis_time:.2f}s",
                    "reframing_time": f"{reframe_time:.2f}s",
                    "total_time": f"{total_time:.2f}s",
                    "video_duration": f"{video_duration:.2f}s",
                    "speed_ratio": f"{speed_ratio:.2f}x",
                    "realtime_capable": speed_ratio < 1.0
                }
            else:
                return {"success": False, "error": "Real-time reframing failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_test_music(self) -> str:
        """Create or find test music"""
        music_path = str(self.temp_dir / "test_music.wav")
        
        if not Path(music_path).exists():
            try:
                import numpy as np
                import scipy.io.wavfile as wavfile
                
                # Create 30-second test music
                sample_rate = 44100
                duration = 30
                t = np.linspace(0, duration, int(sample_rate * duration))
                
                # Simple melody with beats
                audio = (
                    np.sin(2 * np.pi * 440 * t) * 0.3 +  # A note
                    np.sin(2 * np.pi * 330 * t) * 0.2    # E note
                )
                
                # Add beat pattern
                beat_pattern = np.sin(2 * np.pi * 2 * t) > 0  # 2 beats per second
                audio = audio * (0.5 + 0.5 * beat_pattern)
                
                audio = (audio * 32767).astype(np.int16)
                wavfile.write(music_path, sample_rate, audio)
                
                logger.info(f"Created test music: {music_path}")
            except Exception as e:
                logger.warning(f"Could not create test music: {e}")
                return ""
        
        return music_path
    
    def run_full_pipeline(self, video_path: Path, output_name: str) -> Dict:
        """Run complete video processing pipeline"""
        logger.info(f"🎬 Running full pipeline: {video_path.name}")
        
        pipeline_dir = self.output_dir / f"{output_name}_pipeline"
        pipeline_dir.mkdir(exist_ok=True)
        
        try:
            # Create test music
            music_path = self.create_test_music()
            if not music_path:
                return {"success": False, "error": "Could not create test music"}
            
            # Run full pipeline
            import time
            start_time = time.time()
            
            success = self.video_processor.process_video(
                job_id=f"test_{output_name}",
                video_paths=[str(video_path)],
                music_path=music_path,
                style="cinematic",
                output_dir=pipeline_dir,
                enable_ai_reframing=True,
                enable_quality_enhancement=False
            )
            
            duration = time.time() - start_time
            
            if success:
                output_file = pipeline_dir / "output.mp4"
                return {
                    "success": True,
                    "output_file": str(output_file) if output_file.exists() else "Output not found",
                    "processing_time": f"{duration:.1f}s",
                    "pipeline_dir": str(pipeline_dir)
                }
            else:
                return {"success": False, "error": "Pipeline processing failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_tests(self, selected_tests: List[str] = None) -> Dict:
        """Run selected tests on all input videos"""
        if selected_tests is None:
            selected_tests = ["landscape_conversion", "subject_tracking", "realtime_reframing"]
        
        # Discover input videos
        input_videos = self.discover_input_videos()
        
        if not input_videos:
            return {
                "error": f"No videos found in {self.input_dir}. Please add MP4, AVI, or MOV files."
            }
        
        logger.info(f"🎬 Found {len(input_videos)} videos for testing")
        logger.info(f"🧪 Running tests: {', '.join(selected_tests)}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "input_videos": [],
            "test_results": {}
        }
        
        for video_path in input_videos:
            logger.info(f"\\n📹 Testing: {video_path.name}")
            
            # Analyze video
            video_analysis = self.analyze_video(video_path)
            video_name = video_path.stem
            
            video_result = {
                "path": str(video_path),
                "analysis": video_analysis,
                "tests": {}
            }
            
            # Run selected tests
            for test_name in selected_tests:
                if test_name == "landscape_conversion":
                    if video_analysis.get("aspect_ratio", 0) > 1.2:  # Only for landscape videos
                        test_result = self.run_landscape_conversion(video_path, video_name)
                        video_result["tests"][test_name] = test_result
                    else:
                        video_result["tests"][test_name] = {
                            "success": False, 
                            "error": "Not a landscape video (aspect ratio < 1.2)"
                        }
                
                elif test_name == "subject_tracking":
                    test_result = self.run_subject_tracking(video_path, video_name)
                    video_result["tests"][test_name] = test_result
                
                elif test_name == "realtime_reframing":
                    test_result = self.run_realtime_reframing(video_path, video_name)
                    video_result["tests"][test_name] = test_result
                
                elif test_name == "full_pipeline":
                    test_result = self.run_full_pipeline(video_path, video_name)
                    video_result["tests"][test_name] = test_result
            
            results["input_videos"].append(video_result)
            results["test_results"][video_name] = video_result
        
        # Save results
        self.save_results(results)
        self.print_summary(results)
        
        return results
    
    def save_results(self, results: Dict):
        """Save test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"test_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 Results saved: {results_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_summary(self, results: Dict):
        """Print test summary"""
        print("\\n" + "="*80)
        print("🏆 AI REFRAMING TEST RESULTS")
        print("="*80)
        
        total_videos = len(results["input_videos"])
        print(f"📹 Total videos tested: {total_videos}")
        
        # Count test results
        test_counts = {}
        for video_result in results["input_videos"]:
            for test_name, test_result in video_result["tests"].items():
                if test_name not in test_counts:
                    test_counts[test_name] = {"passed": 0, "failed": 0}
                
                if test_result.get("success", False):
                    test_counts[test_name]["passed"] += 1
                else:
                    test_counts[test_name]["failed"] += 1
        
        print(f"\\n📊 Test Summary:")
        for test_name, counts in test_counts.items():
            total = counts["passed"] + counts["failed"]
            success_rate = (counts["passed"] / total * 100) if total > 0 else 0
            print(f"   {test_name}: {counts['passed']}/{total} passed ({success_rate:.1f}%)")
        
        print(f"\\n📁 Output Directory: {self.output_dir}")
        print(f"   - Individual test outputs")
        print(f"   - JSON results file")
        print(f"   - Side-by-side comparisons")
        
        print("\\n✅ Testing complete! Check the output_results folder for all generated videos.")

def main():
    """Main entry point"""
    print("🧪 AI Video Reframing - Easy Test Runner")
    print("="*50)
    
    runner = SimpleTestRunner()
    
    # Check if there are input videos
    input_videos = runner.discover_input_videos()
    
    if not input_videos:
        print(f"📂 No input videos found!")
        print(f"\\n🔧 Setup Instructions:")
        print(f"   1. Copy your video files to: {runner.input_dir}")
        print(f"   2. Supported formats: MP4, AVI, MOV")
        print(f"   3. Run this script again")
        print(f"\\n📖 Check {runner.input_dir}/README.md for detailed instructions")
        return
    
    print(f"📹 Found {len(input_videos)} videos:")
    for i, video in enumerate(input_videos, 1):
        analysis = runner.analyze_video(video)
        size_mb = analysis.get("file_size_mb", 0)
        format_type = analysis.get("format_type", "Unknown")
        dimensions = f"{analysis.get('width', 0)}x{analysis.get('height', 0)}"
        print(f"   {i}. {video.name} ({format_type}, {dimensions}, {size_mb:.1f}MB)")
    
    # Ask user which tests to run
    print(f"\\n🧪 Available Tests:")
    available_tests = {
        "1": "landscape_conversion",
        "2": "subject_tracking", 
        "3": "realtime_reframing",
        "4": "full_pipeline"
    }
    
    for key, test_name in available_tests.items():
        print(f"   {key}. {test_name.replace('_', ' ').title()}")
    
    print(f"   5. All tests")
    
    try:
        choice = input(f"\\n⚡ Select tests to run (1-5, or comma-separated like 1,2,3): ").strip()
        
        if choice == "5":
            selected_tests = list(available_tests.values())
        else:
            selected_indices = [c.strip() for c in choice.split(",")]
            selected_tests = [available_tests[idx] for idx in selected_indices if idx in available_tests]
        
        if not selected_tests:
            print("❌ No valid tests selected. Running all tests.")
            selected_tests = list(available_tests.values())
        
        print(f"\\n🚀 Running: {', '.join(selected_tests)}")
        
        # Run tests
        results = runner.run_tests(selected_tests)
        
    except KeyboardInterrupt:
        print(f"\\n🛑 Testing interrupted by user")
    except Exception as e:
        print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    main()