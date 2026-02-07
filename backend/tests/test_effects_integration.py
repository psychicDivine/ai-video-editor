"""
Integration tests for Effects Service
Tests each effect by:
1. Extracting 5s clips from sample videos
2. Applying effects
3. Merging with transitions
4. Saving output files for inspection
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import logging
from typing import List

from app.services.effects import EffectsService, EFFECT_CATALOG
from app.services.ffmpeg_handler import FFmpegHandler

logger = logging.getLogger(__name__)

# Test configuration
TEST_VIDEO_DIR = Path("test_ip")
TEST_OUTPUT_DIR = Path("test_output/effects")
CLIP_DURATION = 5.0  # 5 seconds per clip


class TestEffectsIntegration:
    """Integration tests for effects service"""
    
    @pytest.fixture(scope="class")
    def setup_test_environment(self):
        """Setup: Create output directory and extract sample clips"""
        # Create output dir
        TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Find sample videos
        sample_videos = list(TEST_VIDEO_DIR.glob("*.mp4"))
        assert len(sample_videos) >= 2, f"Need at least 2 sample videos in {TEST_VIDEO_DIR}"
        
        self.video1_path = str(sample_videos[0])
        self.video2_path = str(sample_videos[1])
        
        # Extract 5-second clips
        self.ffmpeg = FFmpegHandler()
        self.effects = EffectsService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Trim first 5s from each video
            clip1 = temp_path / "clip1.mp4"
            clip2 = temp_path / "clip2.mp4"
            
            success1 = self.ffmpeg.trim_video(
                self.video1_path, str(clip1), 0, CLIP_DURATION,
                width=1080, height=1920
            )
            success2 = self.ffmpeg.trim_video(
                self.video2_path, str(clip2), 0, CLIP_DURATION,
                width=1080, height=1920
            )
            
            assert success1, f"Failed to trim {self.video1_path}"
            assert success2, f"Failed to trim {self.video2_path}"
            
            # Copy to persistent location
            self.clip1_path = TEST_OUTPUT_DIR / "source_clip1.mp4"
            self.clip2_path = TEST_OUTPUT_DIR / "source_clip2.mp4"
            
            shutil.copy(str(clip1), str(self.clip1_path))
            shutil.copy(str(clip2), str(self.clip2_path))
            
            logger.info(f"Created test clips: {self.clip1_path}, {self.clip2_path}")
        
        yield {
            "clip1": self.clip1_path,
            "clip2": self.clip2_path,
            "output_dir": TEST_OUTPUT_DIR
        }
    
    # ============== INDIVIDUAL EFFECT TESTS ==============
    
    @pytest.mark.parametrize("effect_name", [
        "slowmo", "speedup", "speedramp", "freeze",
        "zoomPunch", "kenburns", "flashWhite", "shake",
        "vignette", "colorPulse"
    ])
    def test_effect_individual(self, setup_test_environment, effect_name):
        """Test each effect individually"""
        env = setup_test_environment
        output_file = env["output_dir"] / f"{effect_name}.mp4"
        
        # Get default params for effect
        params = self.effects.get_default_params(effect_name)
        
        # Apply effect
        success = self.effects.apply_effect(
            str(env["clip1"]),
            str(output_file),
            effect_name,
            params
        )
        
        assert success, f"Effect {effect_name} failed to apply"
        assert output_file.exists(), f"Output file not created for {effect_name}"
        assert output_file.stat().st_size > 0, f"Output file empty for {effect_name}"
        
        logger.info(f"✓ {effect_name}: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
    
    # ============== MERGE TESTS ==============
    
    def test_merge_clips_with_transitions(self, setup_test_environment):
        """Test merging two clips with transitions"""
        env = setup_test_environment
        
        # Build per-clip spec
        clips = [
            {
                "path": str(env["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0.5
            },
            {
                "path": str(env["clip2"]),
                "transition_in": "fade",
                "transition_in_duration": 0.5
            }
        ]
        
        output_file = env["output_dir"] / "merged_with_transitions.mp4"
        
        success = self.ffmpeg.concatenate_with_per_clip_transitions(
            clips=clips,
            output_path=str(output_file),
            include_audio=False
        )
        
        assert success, "Failed to merge clips with transitions"
        assert output_file.exists(), "Merged output file not created"
        
        logger.info(f"✓ Merged: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
    
    # ============== SEQUENCE TESTS ==============
    
    def test_all_effects_sequence(self, setup_test_environment):
        """Test applying all effects in sequence"""
        env = setup_test_environment
        
        # List of all effects to apply
        effect_sequence = [
            {"type": "slowmo", "params": {"speed": 0.75}},
            {"type": "zoomPunch", "params": {"intensity": 0.1, "duration": 0.2}},
            {"type": "vignette", "params": {"intensity": 0.2}},
        ]
        
        output_file = env["output_dir"] / "all_effects_sequence.mp4"
        
        success = self.effects.apply_multiple_effects(
            str(env["clip1"]),
            str(output_file),
            effect_sequence
        )
        
        assert success, "Failed to apply effect sequence"
        assert output_file.exists(), "Sequence output not created"
        
        logger.info(f"✓ All effects sequence: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
    
    # ============== STYLE-BASED COMBINATIONS ==============
    
    def test_energetic_dance_style(self, setup_test_environment):
        """Test energetic_dance style effects combination"""
        env = setup_test_environment
        
        # Energetic dance: fast clips, high energy effects
        clips = [
            {
                "path": str(env["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0
            },
            {
                "path": str(env["clip2"]),
                "transition_in": "fadewhite",
                "transition_in_duration": 0.3
            }
        ]
        
        # First merge clips
        merged_file = env["output_dir"] / "temp_energetic_merged.mp4"
        success = self.ffmpeg.concatenate_with_per_clip_transitions(
            clips=clips,
            output_path=str(merged_file),
            include_audio=False
        )
        assert success
        
        # Then apply energetic effects
        output_file = env["output_dir"] / "energetic_dance_style.mp4"
        effects = [
            {"type": "zoomPunch", "params": {"intensity": 0.2, "duration": 0.2}},
            {"type": "shake", "params": {"intensity": 5, "frequency": 20}},
            {"type": "colorPulse", "params": {"intensity": 0.3, "duration": 0.2}},
        ]
        
        success = self.effects.apply_multiple_effects(
            str(merged_file),
            str(output_file),
            effects
        )
        
        assert success, "Failed to apply energetic_dance style"
        assert output_file.exists()
        
        logger.info(f"✓ Energetic dance style: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
        
        # Cleanup temp
        merged_file.unlink(missing_ok=True)
    
    def test_cinematic_drama_style(self, setup_test_environment):
        """Test cinematic_drama style effects combination"""
        env = setup_test_environment
        
        clips = [
            {
                "path": str(env["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0
            },
            {
                "path": str(env["clip2"]),
                "transition_in": "dissolve",
                "transition_in_duration": 0.5
            }
        ]
        
        # Merge clips
        merged_file = env["output_dir"] / "temp_cinematic_merged.mp4"
        success = self.ffmpeg.concatenate_with_per_clip_transitions(
            clips=clips,
            output_path=str(merged_file),
            include_audio=False
        )
        assert success
        
        # Apply cinematic effects
        output_file = env["output_dir"] / "cinematic_drama_style.mp4"
        effects = [
            {"type": "kenburns", "params": {"start_scale": 1.0, "end_scale": 1.1, "direction": "in"}},
            {"type": "vignette", "params": {"intensity": 0.3}},
            {"type": "slowmo", "params": {"speed": 0.8}},
        ]
        
        success = self.effects.apply_multiple_effects(
            str(merged_file),
            str(output_file),
            effects
        )
        
        assert success, "Failed to apply cinematic_drama style"
        assert output_file.exists()
        
        logger.info(f"✓ Cinematic drama style: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
        
        # Cleanup temp
        merged_file.unlink(missing_ok=True)
    
    def test_viral_tiktok_style(self, setup_test_environment):
        """Test viral_tiktok style effects combination"""
        env = setup_test_environment
        
        clips = [
            {
                "path": str(env["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0
            },
            {
                "path": str(env["clip2"]),
                "transition_in": "slideleft",
                "transition_in_duration": 0.3
            }
        ]
        
        # Merge clips
        merged_file = env["output_dir"] / "temp_viral_merged.mp4"
        success = self.ffmpeg.concatenate_with_per_clip_transitions(
            clips=clips,
            output_path=str(merged_file),
            include_audio=False
        )
        assert success
        
        # Apply viral TikTok effects
        output_file = env["output_dir"] / "viral_tiktok_style.mp4"
        effects = [
            {"type": "zoomPunch", "params": {"intensity": 0.25, "duration": 0.2}},
            {"type": "flashWhite", "params": {"duration": 0.15, "intensity": 0.9}},
            {"type": "shake", "params": {"intensity": 8, "frequency": 25}},
        ]
        
        success = self.effects.apply_multiple_effects(
            str(merged_file),
            str(output_file),
            effects
        )
        
        assert success, "Failed to apply viral_tiktok style"
        assert output_file.exists()
        
        logger.info(f"✓ Viral TikTok style: {output_file.stat().st_size / 1024 / 1024:.1f}MB")
        
        # Cleanup temp
        merged_file.unlink(missing_ok=True)
    
    # ============== TRANSITION TESTS ==============
    
    @pytest.mark.parametrize("transition_type", [
        "fade", "dissolve", "fadeblack", "fadewhite",
        "wipeleft", "wiperight", "slideleft", "slideright",
        "circlecrop", "pixelize"
    ])
    def test_transition_type(self, setup_test_environment, transition_type):
        """Test each transition type"""
        env = setup_test_environment
        
        clips = [
            {
                "path": str(env["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0
            },
            {
                "path": str(env["clip2"]),
                "transition_in": transition_type,
                "transition_in_duration": 0.5
            }
        ]
        
        output_file = env["output_dir"] / f"transition_{transition_type}.mp4"
        
        success = self.ffmpeg.concatenate_with_per_clip_transitions(
            clips=clips,
            output_path=str(output_file),
            include_audio=False
        )
        
        assert success, f"Transition {transition_type} failed"
        assert output_file.exists(), f"Transition output not created for {transition_type}"
        
        logger.info(f"✓ {transition_type}: {output_file.stat().st_size / 1024 / 1024:.1f}MB")


if __name__ == "__main__":
    # Run tests: pytest backend/tests/test_effects_integration.py -v -s
    pytest.main([__file__, "-v", "-s"])
