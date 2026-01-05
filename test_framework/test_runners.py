#!/usr/bin/env python3
"""
Test Runners for AI Video Reframing
Specific test implementations for different scenarios
"""
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import cv2
import numpy as np

from .video_test_suite import TestType, TestResult, TestVideo, VideoTestSuite

logger = logging.getLogger(__name__)

class LandscapeConversionTest:
    """Test landscape to portrait conversion"""
    
    def __init__(self, test_suite: VideoTestSuite):
        self.test_suite = test_suite
    
    def run_test(self, test_video: TestVideo) -> TestResult:
        """Run landscape conversion test"""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            # Output path
            output_path = str(self.test_suite.results_dir / f"{test_video.name}_landscape_converted.mp4")
            
            logger.info(f"Testing landscape conversion: {test_video.name}")
            
            # Check if video is actually landscape
            is_landscape = test_video.width > test_video.height
            if not is_landscape:
                errors.append(f"Input video is not landscape ({test_video.width}x{test_video.height})")
                return self._create_result(
                    "Landscape Conversion", test_video, output_path, 
                    False, time.time() - start_time, metrics, errors
                )
            
            # Analyze video for reframing
            analyses = self.test_suite.ai_reframing.analyze_video_for_reframing(
                test_video.path, sample_rate=10
            )
            
            if not analyses:
                errors.append("Failed to analyze video for reframing")
                return self._create_result(
                    "Landscape Conversion", test_video, output_path,
                    False, time.time() - start_time, metrics, errors
                )
            
            # Get analysis stats
            stats = self.test_suite.ai_reframing.get_reframing_stats(analyses)
            metrics.update(stats)
            
            # Apply smart reframing
            success = self.test_suite.ai_reframing.apply_smart_reframing(
                test_video.path, output_path, analyses
            )
            
            if success:
                # Verify output dimensions
                output_info = self.test_suite.ffmpeg.get_video_info(output_path)
                if output_info:
                    output_width = output_info.get("width", 0)
                    output_height = output_info.get("height", 0)
                    
                    metrics["output_width"] = output_width
                    metrics["output_height"] = output_height
                    metrics["aspect_ratio"] = output_width / output_height if output_height > 0 else 0
                    
                    # Check if conversion was successful (should be 9:16 aspect ratio)
                    expected_ratio = 9/16
                    actual_ratio = output_width / output_height if output_height > 0 else 0
                    ratio_error = abs(actual_ratio - expected_ratio)
                    
                    metrics["aspect_ratio_error"] = ratio_error
                    
                    if ratio_error < 0.01:  # Allow small tolerance
                        logger.info(f"✅ Landscape conversion successful: {test_video.name}")
                    else:
                        errors.append(f"Aspect ratio error: expected {expected_ratio:.3f}, got {actual_ratio:.3f}")
                        success = False
                else:
                    errors.append("Could not verify output video properties")
                    success = False
            else:
                errors.append("Smart reframing failed")
            
            return self._create_result(
                "Landscape Conversion", test_video, output_path,
                success, time.time() - start_time, metrics, errors
            )
            
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
            return self._create_result(
                "Landscape Conversion", test_video, "",
                False, time.time() - start_time, metrics, errors
            )
    
    def _create_result(
        self, test_name: str, test_video: TestVideo, output_path: str,
        success: bool, duration: float, metrics: Dict, errors: List[str]
    ) -> TestResult:
        return TestResult(
            test_name=test_name,
            test_type=TestType.LANDSCAPE_CONVERSION,
            input_video=test_video.path,
            output_video=output_path,
            success=success,
            duration=duration,
            metrics=metrics,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )

class SubjectTrackingTest:
    """Test subject detection and tracking"""
    
    def __init__(self, test_suite: VideoTestSuite):
        self.test_suite = test_suite
    
    def run_test(self, test_video: TestVideo) -> TestResult:
        """Run subject tracking test"""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            output_path = str(self.test_suite.results_dir / f"{test_video.name}_subject_tracked.mp4")
            
            logger.info(f"Testing subject tracking: {test_video.name}")
            
            # Analyze with detailed frame sampling for subject tracking
            analyses = self.test_suite.ai_reframing.analyze_video_for_reframing(
                test_video.path, sample_rate=5  # More frequent sampling for better tracking
            )
            
            if not analyses:
                errors.append("Failed to analyze video for subject tracking")
                return self._create_result(
                    "Subject Tracking", test_video, output_path,
                    False, time.time() - start_time, metrics, errors
                )
            
            # Analyze subject detection performance
            frames_with_subjects = sum(1 for a in analyses if a.primary_subject is not None)
            total_frames = len(analyses)
            detection_rate = frames_with_subjects / total_frames if total_frames > 0 else 0
            
            metrics["frames_analyzed"] = total_frames
            metrics["frames_with_subjects"] = frames_with_subjects
            metrics["subject_detection_rate"] = detection_rate
            
            # Track subject consistency (how much the primary subject moves)
            if frames_with_subjects > 1:
                subject_positions = []
                for analysis in analyses:
                    if analysis.primary_subject:
                        subject_positions.append((
                            analysis.primary_subject.center_x,
                            analysis.primary_subject.center_y
                        ))
                
                if len(subject_positions) > 1:
                    # Calculate movement variance
                    positions = np.array(subject_positions)
                    x_variance = np.var(positions[:, 0])
                    y_variance = np.var(positions[:, 1])
                    total_variance = x_variance + y_variance
                    
                    metrics["subject_x_variance"] = float(x_variance)
                    metrics["subject_y_variance"] = float(y_variance)
                    metrics["subject_position_variance"] = float(total_variance)
                    
                    # Check if tracking is smooth (low variance is better for reframing)
                    if total_variance < 10000:  # Arbitrary threshold
                        metrics["tracking_quality"] = "smooth"
                    else:
                        metrics["tracking_quality"] = "jittery"
            
            # Apply reframing with subject tracking
            success = self.test_suite.ai_reframing.apply_smart_reframing(
                test_video.path, output_path, analyses
            )
            
            if success:
                # Verify that subject tracking influenced the reframing
                crop_bounds_variance = self._analyze_crop_consistency(analyses)
                metrics["crop_consistency"] = crop_bounds_variance
                
                logger.info(f"✅ Subject tracking test completed: {test_video.name}")
            else:
                errors.append("Subject tracking reframing failed")
            
            # Evaluate based on expected subjects
            if test_video.expected_subjects > 0:
                if detection_rate >= 0.7:  # Expect to detect subjects in at least 70% of frames
                    metrics["detection_performance"] = "good"
                elif detection_rate >= 0.3:
                    metrics["detection_performance"] = "fair"
                    errors.append(f"Low subject detection rate: {detection_rate:.2%}")
                else:
                    metrics["detection_performance"] = "poor"
                    errors.append(f"Very low subject detection rate: {detection_rate:.2%}")
                    success = False
            
            return self._create_result(
                "Subject Tracking", test_video, output_path,
                success, time.time() - start_time, metrics, errors
            )
            
        except Exception as e:
            errors.append(f"Subject tracking test error: {str(e)}")
            return self._create_result(
                "Subject Tracking", test_video, "",
                False, time.time() - start_time, metrics, errors
            )
    
    def _analyze_crop_consistency(self, analyses) -> float:
        """Analyze how consistent the crop bounds are across frames"""
        if len(analyses) < 2:
            return 0.0
        
        crop_centers = []
        for analysis in analyses:
            x1, y1, x2, y2 = analysis.crop_bounds
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            crop_centers.append((center_x, center_y))
        
        if len(crop_centers) > 1:
            centers = np.array(crop_centers)
            variance = np.var(centers[:, 0]) + np.var(centers[:, 1])
            return float(variance)
        
        return 0.0
    
    def _create_result(
        self, test_name: str, test_video: TestVideo, output_path: str,
        success: bool, duration: float, metrics: Dict, errors: List[str]
    ) -> TestResult:
        return TestResult(
            test_name=test_name,
            test_type=TestType.SUBJECT_TRACKING,
            input_video=test_video.path,
            output_video=output_path,
            success=success,
            duration=duration,
            metrics=metrics,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )

class RealtimeReframingTest:
    """Test real-time reframing with moving subjects"""
    
    def __init__(self, test_suite: VideoTestSuite):
        self.test_suite = test_suite
    
    def run_test(self, test_video: TestVideo) -> TestResult:
        """Run real-time reframing test"""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            output_path = str(self.test_suite.results_dir / f"{test_video.name}_realtime_reframed.mp4")
            
            logger.info(f"Testing real-time reframing: {test_video.name}")
            
            # High-frequency analysis for real-time simulation
            analyses = self.test_suite.ai_reframing.analyze_video_for_reframing(
                test_video.path, sample_rate=2  # Analyze every 2nd frame for "real-time"
            )
            
            if not analyses:
                errors.append("Failed to analyze video for real-time reframing")
                return self._create_result(
                    "Real-time Reframing", test_video, output_path,
                    False, time.time() - start_time, metrics, errors
                )
            
            analysis_time = time.time() - start_time
            frames_per_second = len(analyses) / analysis_time if analysis_time > 0 else 0
            
            metrics["analysis_fps"] = frames_per_second
            metrics["frames_analyzed"] = len(analyses)
            metrics["analysis_duration"] = analysis_time
            
            # Check if analysis is fast enough for "real-time" (should be faster than video FPS)
            expected_fps = test_video.fps
            if frames_per_second >= expected_fps * 0.5:  # At least 50% of video FPS
                metrics["realtime_capable"] = True
            else:
                metrics["realtime_capable"] = False
                errors.append(f"Analysis too slow for real-time: {frames_per_second:.1f} fps vs {expected_fps} fps required")
            
            # Test frame-by-frame consistency for smooth reframing
            engagement_scores = [a.engagement_score for a in analyses]
            if len(engagement_scores) > 1:
                engagement_variance = np.var(engagement_scores)
                metrics["engagement_consistency"] = float(engagement_variance)
                
                # Check for sudden jumps in engagement (indicates instability)
                engagement_diffs = np.diff(engagement_scores)
                max_diff = np.max(np.abs(engagement_diffs)) if len(engagement_diffs) > 0 else 0
                metrics["max_engagement_jump"] = float(max_diff)
                
                if max_diff > 0.3:  # Large sudden change in engagement score
                    errors.append(f"Unstable engagement detection: max jump {max_diff:.3f}")
            
            # Apply reframing
            reframe_start = time.time()
            success = self.test_suite.ai_reframing.apply_smart_reframing(
                test_video.path, output_path, analyses
            )
            reframe_duration = time.time() - reframe_start
            
            metrics["reframing_duration"] = reframe_duration
            metrics["total_processing_time"] = analysis_time + reframe_duration
            
            # Calculate processing speed ratio (processing time vs video duration)
            processing_ratio = (analysis_time + reframe_duration) / test_video.duration
            metrics["processing_speed_ratio"] = processing_ratio
            
            if processing_ratio < 1.0:
                metrics["faster_than_realtime"] = True
            else:
                metrics["faster_than_realtime"] = False
                if processing_ratio > 2.0:  # More than 2x video duration
                    errors.append(f"Processing too slow: {processing_ratio:.1f}x video duration")
            
            if success:
                logger.info(f"✅ Real-time reframing test completed: {test_video.name}")
                logger.info(f"   Processing speed: {processing_ratio:.2f}x video duration")
                logger.info(f"   Analysis FPS: {frames_per_second:.1f}")
            else:
                errors.append("Real-time reframing failed")
            
            return self._create_result(
                "Real-time Reframing", test_video, output_path,
                success, time.time() - start_time, metrics, errors
            )
            
        except Exception as e:
            errors.append(f"Real-time reframing test error: {str(e)}")
            return self._create_result(
                "Real-time Reframing", test_video, "",
                False, time.time() - start_time, metrics, errors
            )
    
    def _create_result(
        self, test_name: str, test_video: TestVideo, output_path: str,
        success: bool, duration: float, metrics: Dict, errors: List[str]
    ) -> TestResult:
        return TestResult(
            test_name=test_name,
            test_type=TestType.REALTIME_REFRAMING,
            input_video=test_video.path,
            output_video=output_path,
            success=success,
            duration=duration,
            metrics=metrics,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )