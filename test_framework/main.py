#!/usr/bin/env python3
"""
AI Video Reframing Test Framework - Main Runner
Comprehensive testing system for landscape conversion, subject tracking, and real-time reframing
"""
import logging
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from test_framework.video_test_suite import VideoTestSuite, TestType, VideoType, TestResult, TestSuiteResults
from test_framework.test_runners import LandscapeConversionTest, SubjectTrackingTest, RealtimeReframingTest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIVideoTestRunner:
    """Main test runner for AI video reframing tests"""
    
    def __init__(self):
        """Initialize the test runner"""
        self.test_suite = VideoTestSuite()
        
        # Initialize test runners
        self.landscape_test = LandscapeConversionTest(self.test_suite)
        self.subject_test = SubjectTrackingTest(self.test_suite)
        self.realtime_test = RealtimeReframingTest(self.test_suite)
        
        self.all_results: List[TestResult] = []
    
    def setup_test_environment(self):
        """Set up test environment with sample videos"""
        logger.info("🚀 Setting up AI video test environment...")
        
        # Create synthetic test videos
        self.test_suite.create_test_videos()
        
        logger.info(f"✅ Test environment ready with {len(self.test_suite.test_videos)} test videos")
        
        # List available test videos
        logger.info("📹 Available test videos:")
        for video in self.test_suite.test_videos:
            logger.info(f"  - {video.name} ({video.video_type.value}): {video.width}x{video.height}")
    
    def run_landscape_conversion_tests(self, video_filter: Optional[str] = None) -> List[TestResult]:
        """Run landscape to portrait conversion tests"""
        logger.info("🔄 Running Landscape Conversion Tests...")
        
        landscape_videos = [
            v for v in self.test_suite.test_videos
            if v.width > v.height  # Only landscape videos
            and (not video_filter or video_filter.lower() in v.name.lower())
        ]
        
        if not landscape_videos:
            logger.warning("⚠️ No landscape videos found for testing")
            return []
        
        results = []
        for video in landscape_videos:
            logger.info(f"Testing landscape conversion: {video.name}")
            result = self.landscape_test.run_test(video)
            results.append(result)
            
            if result.success:
                logger.info(f"✅ {video.name}: PASSED")
                logger.info(f"   Aspect ratio: {result.metrics.get('aspect_ratio', 'N/A'):.3f}")
                logger.info(f"   Subject detection: {result.metrics.get('subject_detection_rate', 0):.1%}")
            else:
                logger.error(f"❌ {video.name}: FAILED")
                for error in result.errors:
                    logger.error(f"   - {error}")
        
        self.all_results.extend(results)
        return results
    
    def run_subject_tracking_tests(self, video_filter: Optional[str] = None) -> List[TestResult]:
        """Run subject detection and tracking tests"""
        logger.info("👁️ Running Subject Tracking Tests...")
        
        subject_videos = [
            v for v in self.test_suite.test_videos
            if v.expected_subjects > 0 or v.has_motion
            and (not video_filter or video_filter.lower() in v.name.lower())
        ]
        
        if not subject_videos:
            # If no specific subject videos, test all videos for subject detection capability
            subject_videos = [
                v for v in self.test_suite.test_videos
                if not video_filter or video_filter.lower() in v.name.lower()
            ]
        
        results = []
        for video in subject_videos:
            logger.info(f"Testing subject tracking: {video.name}")
            result = self.subject_test.run_test(video)
            results.append(result)
            
            if result.success:
                logger.info(f"✅ {video.name}: PASSED")
                detection_rate = result.metrics.get('subject_detection_rate', 0)
                logger.info(f"   Subject detection rate: {detection_rate:.1%}")
                
                tracking_quality = result.metrics.get('tracking_quality', 'unknown')
                logger.info(f"   Tracking quality: {tracking_quality}")
            else:
                logger.error(f"❌ {video.name}: FAILED")
                for error in result.errors:
                    logger.error(f"   - {error}")
        
        self.all_results.extend(results)
        return results
    
    def run_realtime_reframing_tests(self, video_filter: Optional[str] = None) -> List[TestResult]:
        """Run real-time reframing performance tests"""
        logger.info("⚡ Running Real-time Reframing Tests...")
        
        test_videos = [
            v for v in self.test_suite.test_videos
            if not video_filter or video_filter.lower() in v.name.lower()
        ]
        
        results = []
        for video in test_videos:
            logger.info(f"Testing real-time reframing: {video.name}")
            result = self.realtime_test.run_test(video)
            results.append(result)
            
            if result.success:
                logger.info(f"✅ {video.name}: PASSED")
                
                processing_ratio = result.metrics.get('processing_speed_ratio', float('inf'))
                analysis_fps = result.metrics.get('analysis_fps', 0)
                
                logger.info(f"   Processing speed: {processing_ratio:.2f}x video duration")
                logger.info(f"   Analysis FPS: {analysis_fps:.1f}")
                
                if result.metrics.get('realtime_capable'):
                    logger.info(f"   🚀 Real-time capable!")
                else:
                    logger.info(f"   ⚠️ Not real-time capable")
            else:
                logger.error(f"❌ {video.name}: FAILED")
                for error in result.errors:
                    logger.error(f"   - {error}")
        
        self.all_results.extend(results)
        return results
    
    def run_full_pipeline_tests(self, video_filter: Optional[str] = None) -> List[TestResult]:
        """Run complete pipeline tests (like production workflow)"""
        logger.info("🔄 Running Full Pipeline Tests...")
        
        test_videos = [
            v for v in self.test_suite.test_videos
            if not video_filter or video_filter.lower() in v.name.lower()
        ][:2]  # Limit to 2 videos for full pipeline (it's slower)
        
        results = []
        
        # Create a simple music file for testing
        music_path = self._create_test_music()
        
        for video in test_videos:
            logger.info(f"Testing full pipeline: {video.name}")
            
            try:
                start_time = datetime.now()
                
                # Run through the complete video processor pipeline
                output_dir = Path("test_framework/results") / f"pipeline_{video.name}"
                output_dir.mkdir(exist_ok=True, parents=True)
                
                success = self.test_suite.video_processor.process_video(
                    job_id=f"test_{video.name}",
                    video_paths=[video.path],
                    music_path=music_path,
                    style="cinematic",
                    output_dir=output_dir,
                    enable_ai_reframing=True,
                    enable_quality_enhancement=False  # Skip for speed
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                metrics = {
                    "pipeline_duration": duration,
                    "processing_speed_ratio": duration / video.duration if video.duration > 0 else float('inf')
                }
                
                errors = [] if success else ["Full pipeline processing failed"]
                
                result = TestResult(
                    test_name="Full Pipeline",
                    test_type=TestType.FULL_PIPELINE,
                    input_video=video.path,
                    output_video=str(output_dir / "output.mp4") if success else "",
                    success=success,
                    duration=duration,
                    metrics=metrics,
                    errors=errors,
                    timestamp=start_time.isoformat()
                )
                
                results.append(result)
                
                if success:
                    logger.info(f"✅ {video.name}: PASSED")
                    logger.info(f"   Pipeline duration: {duration:.1f}s")
                    logger.info(f"   Output: {result.output_video}")
                else:
                    logger.error(f"❌ {video.name}: FAILED")
                
            except Exception as e:
                logger.error(f"❌ {video.name}: ERROR - {str(e)}")
                
                result = TestResult(
                    test_name="Full Pipeline",
                    test_type=TestType.FULL_PIPELINE,
                    input_video=video.path,
                    output_video="",
                    success=False,
                    duration=0,
                    metrics={},
                    errors=[f"Pipeline error: {str(e)}"],
                    timestamp=datetime.now().isoformat()
                )
                results.append(result)
        
        self.all_results.extend(results)
        return results
    
    def _create_test_music(self) -> str:
        """Create a simple test music file"""
        music_path = "test_framework/results/test_music.wav"
        
        if not Path(music_path).exists():
            try:
                # Create simple sine wave music using numpy
                import numpy as np
                import scipy.io.wavfile as wavfile
                
                sample_rate = 44100
                duration = 30  # 30 seconds
                frequency = 440  # A note
                
                t = np.linspace(0, duration, int(sample_rate * duration))
                audio = np.sin(2 * np.pi * frequency * t) * 0.3  # Lower volume
                
                # Add some variation
                audio += np.sin(2 * np.pi * frequency * 1.5 * t) * 0.2
                
                # Convert to 16-bit PCM
                audio = (audio * 32767).astype(np.int16)
                
                wavfile.write(music_path, sample_rate, audio)
                logger.info(f"Created test music: {music_path}")
                
            except Exception as e:
                logger.warning(f"Failed to create test music: {e}")
                # Use existing music file if available
                existing_music = list(Path("backend/uploads").rglob("*.mp3"))
                if existing_music:
                    music_path = str(existing_music[0])
                    logger.info(f"Using existing music: {music_path}")
        
        return music_path
    
    def run_all_tests(self, video_filter: Optional[str] = None) -> TestSuiteResults:
        """Run complete test suite"""
        logger.info("🧪 Running Complete AI Video Reframing Test Suite")
        
        start_time = datetime.now()
        self.all_results = []
        
        # Setup environment
        self.setup_test_environment()
        
        # Run all test categories
        landscape_results = self.run_landscape_conversion_tests(video_filter)
        subject_results = self.run_subject_tracking_tests(video_filter)
        realtime_results = self.run_realtime_reframing_tests(video_filter)
        pipeline_results = self.run_full_pipeline_tests(video_filter)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # Generate summary
        total_tests = len(self.all_results)
        passed_tests = sum(1 for r in self.all_results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Category breakdown
        summary = {
            "landscape_conversion": {
                "total": len(landscape_results),
                "passed": sum(1 for r in landscape_results if r.success),
                "avg_aspect_ratio": self._avg_metric(landscape_results, "aspect_ratio")
            },
            "subject_tracking": {
                "total": len(subject_results),
                "passed": sum(1 for r in subject_results if r.success),
                "avg_detection_rate": self._avg_metric(subject_results, "subject_detection_rate")
            },
            "realtime_reframing": {
                "total": len(realtime_results),
                "passed": sum(1 for r in realtime_results if r.success),
                "avg_processing_speed": self._avg_metric(realtime_results, "processing_speed_ratio"),
                "realtime_capable_count": sum(1 for r in realtime_results if r.metrics.get("realtime_capable", False))
            },
            "full_pipeline": {
                "total": len(pipeline_results),
                "passed": sum(1 for r in pipeline_results if r.success),
                "avg_pipeline_duration": self._avg_metric(pipeline_results, "pipeline_duration")
            }
        }
        
        results = TestSuiteResults(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_duration=total_duration,
            results=self.all_results,
            summary=summary
        )
        
        # Save results
        self._save_results(results)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _avg_metric(self, results: List[TestResult], metric_name: str) -> float:
        """Calculate average value for a metric"""
        values = [r.metrics.get(metric_name, 0) for r in results if r.success and metric_name in r.metrics]
        return sum(values) / len(values) if values else 0.0
    
    def _save_results(self, results: TestSuiteResults):
        """Save test results to file"""
        results_file = Path("test_framework/results") / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True, parents=True)
        
        try:
            # Convert results to serializable format
            results_dict = {
                "total_tests": results.total_tests,
                "passed_tests": results.passed_tests,
                "failed_tests": results.failed_tests,
                "total_duration": results.total_duration,
                "summary": results.summary,
                "results": [
                    {
                        "test_name": r.test_name,
                        "test_type": r.test_type.value,
                        "input_video": r.input_video,
                        "output_video": r.output_video,
                        "success": r.success,
                        "duration": r.duration,
                        "metrics": r.metrics,
                        "errors": r.errors,
                        "timestamp": r.timestamp
                    }
                    for r in results.results
                ]
            }
            
            with open(results_file, 'w') as f:
                json.dump(results_dict, f, indent=2)
            
            logger.info(f"📄 Test results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
    
    def _print_summary(self, results: TestSuiteResults):
        """Print test summary"""
        logger.info("="*80)
        logger.info("🏆 AI VIDEO REFRAMING TEST RESULTS")
        logger.info("="*80)
        
        logger.info(f"📊 Overall Results:")
        logger.info(f"   Total Tests: {results.total_tests}")
        logger.info(f"   Passed: {results.passed_tests} ✅")
        logger.info(f"   Failed: {results.failed_tests} ❌")
        logger.info(f"   Success Rate: {results.passed_tests/results.total_tests*100:.1f}%" if results.total_tests > 0 else "   Success Rate: N/A")
        logger.info(f"   Total Duration: {results.total_duration:.1f}s")
        
        logger.info(f"\\n📈 Category Breakdown:")
        
        for category, stats in results.summary.items():
            success_rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
            logger.info(f"   {category.replace('_', ' ').title()}:")
            logger.info(f"      {stats['passed']}/{stats['total']} passed ({success_rate:.1f}%)")
            
            # Category-specific metrics
            if category == "landscape_conversion" and stats.get('avg_aspect_ratio'):
                logger.info(f"      Avg aspect ratio: {stats['avg_aspect_ratio']:.3f} (target: 0.563)")
            elif category == "subject_tracking" and stats.get('avg_detection_rate'):
                logger.info(f"      Avg detection rate: {stats['avg_detection_rate']:.1%}")
            elif category == "realtime_reframing":
                if stats.get('avg_processing_speed'):
                    logger.info(f"      Avg processing speed: {stats['avg_processing_speed']:.2f}x video duration")
                logger.info(f"      Real-time capable: {stats['realtime_capable_count']}/{stats['total']}")
            elif category == "full_pipeline" and stats.get('avg_pipeline_duration'):
                logger.info(f"      Avg pipeline duration: {stats['avg_pipeline_duration']:.1f}s")
        
        logger.info("="*80)
        
        if results.passed_tests == results.total_tests:
            logger.info("🎉 ALL TESTS PASSED! AI reframing system is working perfectly!")
        elif results.passed_tests > results.total_tests * 0.8:
            logger.info("✅ Most tests passed! AI reframing system is working well.")
        else:
            logger.warning("⚠️ Some tests failed. Check individual results for details.")

def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Reframing Test Framework")
    parser.add_argument("--test-type", choices=["landscape", "subject", "realtime", "pipeline", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--video-filter", type=str, help="Filter videos by name (substring match)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    runner = AIVideoTestRunner()
    
    try:
        if args.test_type == "all":
            results = runner.run_all_tests(args.video_filter)
        elif args.test_type == "landscape":
            runner.setup_test_environment()
            results = runner.run_landscape_conversion_tests(args.video_filter)
        elif args.test_type == "subject":
            runner.setup_test_environment()
            results = runner.run_subject_tracking_tests(args.video_filter)
        elif args.test_type == "realtime":
            runner.setup_test_environment()
            results = runner.run_realtime_reframing_tests(args.video_filter)
        elif args.test_type == "pipeline":
            runner.setup_test_environment()
            results = runner.run_full_pipeline_tests(args.video_filter)
        
        # Exit with appropriate code
        if hasattr(results, 'failed_tests'):
            sys.exit(0 if results.failed_tests == 0 else 1)
        else:
            success_count = sum(1 for r in results if r.success) if isinstance(results, list) else 0
            sys.exit(0 if success_count == len(results) else 1)
            
    except KeyboardInterrupt:
        logger.info("\\n🛑 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()