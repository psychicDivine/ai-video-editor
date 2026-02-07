"""
Simple Effects Test Runner - No pytest required
Extracts 5s clips and tests all effects
Run: python tests/test_effects_simple.py
"""
import sys
from pathlib import Path
import tempfile
import shutil
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.effects import EffectsService, EFFECT_CATALOG
from app.services.ffmpeg_handler import FFmpegHandler

# Configuration
TEST_VIDEO_DIR = Path(__file__).parent.parent.parent / "test_ip"
TEST_OUTPUT_DIR = Path(__file__).parent.parent.parent / "test_output" / "effects"
CLIP_DURATION = 5.0


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_success(text):
    print(f"✓ {text}")


def print_error(text):
    print(f"✗ {text}")


def setup_test_clips():
    """Extract first 5 seconds from both sample videos"""
    print_header("SETUP: Creating Test Clips")
    
    # Find sample videos
    sample_videos = list(TEST_VIDEO_DIR.glob("*.mp4"))
    if len(sample_videos) < 2:
        print_error(f"Need at least 2 videos in {TEST_VIDEO_DIR}")
        return None
    
    video1 = sample_videos[0]
    video2 = sample_videos[1]
    print(f"Found videos: {video1.name}, {video2.name}")
    
    # Create output dir
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    ffmpeg = FFmpegHandler()
    
    # Trim clips
    clip1_path = TEST_OUTPUT_DIR / "source_clip1.mp4"
    clip2_path = TEST_OUTPUT_DIR / "source_clip2.mp4"
    
    print(f"\nTrimming {CLIP_DURATION}s from {video1.name}...")
    success1 = ffmpeg.trim_video(
        str(video1), str(clip1_path), 0, CLIP_DURATION,
        width=1080, height=1920
    )
    
    print(f"Trimming {CLIP_DURATION}s from {video2.name}...")
    success2 = ffmpeg.trim_video(
        str(video2), str(clip2_path), 0, CLIP_DURATION,
        width=1080, height=1920
    )
    
    if success1 and success2:
        size1 = clip1_path.stat().st_size / 1024 / 1024
        size2 = clip2_path.stat().st_size / 1024 / 1024
        print_success(f"Clip 1: {clip1_path.name} ({size1:.1f}MB)")
        print_success(f"Clip 2: {clip2_path.name} ({size2:.1f}MB)")
        return {"clip1": clip1_path, "clip2": clip2_path}
    else:
        print_error("Failed to create test clips")
        return None


def test_individual_effects(clips):
    """Test each effect individually"""
    print_header("TEST 1: Individual Effects")
    
    effects = EffectsService()
    results = {}
    
    effect_list = [
        "slowmo", "speedup", "speedramp", "freeze",
        "zoomPunch", "kenburns", "flashWhite", "shake",
        "vignette", "colorPulse"
    ]
    
    for effect_name in effect_list:
        output_file = TEST_OUTPUT_DIR / f"{effect_name}.mp4"
        params = effects.get_default_params(effect_name)
        
        start_time = time.time()
        success = effects.apply_effect(
            str(clips["clip1"]),
            str(output_file),
            effect_name,
            params
        )
        elapsed = time.time() - start_time
        
        if success and output_file.exists():
            size = output_file.stat().st_size / 1024 / 1024
            print_success(f"{effect_name:15} {size:7.1f}MB ({elapsed:.1f}s)")
            results[effect_name] = True
        else:
            print_error(f"{effect_name:15} FAILED")
            results[effect_name] = False
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nResult: {passed}/{total} effects passed")
    return results


def test_transitions(clips):
    """Test merging clips with different transitions"""
    print_header("TEST 2: Transitions")
    
    ffmpeg = FFmpegHandler()
    results = {}
    
    transition_list = [
        "fade", "dissolve", "fadeblack", "fadewhite",
        "wipeleft", "wiperight", "slideleft", "slideright",
        "circlecrop", "pixelize"
    ]
    
    for trans in transition_list:
        output_file = TEST_OUTPUT_DIR / f"transition_{trans}.mp4"
        
        clip_specs = [
            {
                "path": str(clips["clip1"]),
                "transition_in": None,
                "transition_in_duration": 0
            },
            {
                "path": str(clips["clip2"]),
                "transition_in": trans,
                "transition_in_duration": 0.5
            }
        ]
        
        start_time = time.time()
        success = ffmpeg.concatenate_with_per_clip_transitions(
            clips=clip_specs,
            output_path=str(output_file),
            include_audio=False
        )
        elapsed = time.time() - start_time
        
        if success and output_file.exists():
            size = output_file.stat().st_size / 1024 / 1024
            print_success(f"{trans:15} {size:7.1f}MB ({elapsed:.1f}s)")
            results[trans] = True
        else:
            print_error(f"{trans:15} FAILED")
            results[trans] = False
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nResult: {passed}/{total} transitions passed")
    return results


def test_style_combinations(clips):
    """Test style-based effect combinations"""
    print_header("TEST 3: Style Combinations")
    
    ffmpeg = FFmpegHandler()
    effects = EffectsService()
    results = {}
    
    styles = {
        "energetic_dance": {
            "transitions": [None, "fadewhite"],
            "effects": [
                {"type": "zoomPunch", "params": {"intensity": 0.2, "duration": 0.2}},
                {"type": "shake", "params": {"intensity": 5, "frequency": 20}},
                {"type": "colorPulse", "params": {"intensity": 0.3, "duration": 0.2}},
            ]
        },
        "cinematic_drama": {
            "transitions": [None, "dissolve"],
            "effects": [
                {"type": "kenburns", "params": {"start_scale": 1.0, "end_scale": 1.1, "direction": "in"}},
                {"type": "vignette", "params": {"intensity": 0.3}},
                {"type": "slowmo", "params": {"speed": 0.8}},
            ]
        },
        "viral_tiktok": {
            "transitions": [None, "slideleft"],
            "effects": [
                {"type": "zoomPunch", "params": {"intensity": 0.25, "duration": 0.2}},
                {"type": "flashWhite", "params": {"duration": 0.15, "intensity": 0.9}},
                {"type": "shake", "params": {"intensity": 8, "frequency": 25}},
            ]
        }
    }
    
    for style_name, style_config in styles.items():
        output_file = TEST_OUTPUT_DIR / f"{style_name}_style.mp4"
        
        # Merge clips with transitions
        clip_specs = [
            {
                "path": str(clips["clip1"]),
                "transition_in": style_config["transitions"][0],
                "transition_in_duration": 0
            },
            {
                "path": str(clips["clip2"]),
                "transition_in": style_config["transitions"][1],
                "transition_in_duration": 0.5
            }
        ]
        
        temp_merged = TEST_OUTPUT_DIR / f"temp_{style_name}_merged.mp4"
        
        success = ffmpeg.concatenate_with_per_clip_transitions(
            clips=clip_specs,
            output_path=str(temp_merged),
            include_audio=False
        )
        
        if not success:
            print_error(f"{style_name:20} FAILED (merge)")
            results[style_name] = False
            continue
        
        # Apply effects
        start_time = time.time()
        success = effects.apply_multiple_effects(
            str(temp_merged),
            str(output_file),
            style_config["effects"]
        )
        elapsed = time.time() - start_time
        
        # Cleanup temp
        temp_merged.unlink(missing_ok=True)
        
        if success and output_file.exists():
            size = output_file.stat().st_size / 1024 / 1024
            print_success(f"{style_name:20} {size:7.1f}MB ({elapsed:.1f}s)")
            results[style_name] = True
        else:
            print_error(f"{style_name:20} FAILED")
            results[style_name] = False
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nResult: {passed}/{total} styles passed")
    return results


def main():
    print_header("EFFECTS INTEGRATION TEST")
    print(f"Test Videos: {TEST_VIDEO_DIR}")
    print(f"Output Dir:  {TEST_OUTPUT_DIR}")
    
    # Setup
    clips = setup_test_clips()
    if not clips:
        print_error("Setup failed, aborting")
        return
    
    # Run tests
    results_effects = test_individual_effects(clips)
    results_transitions = test_transitions(clips)
    results_styles = test_style_combinations(clips)
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_passed = (
        sum(1 for v in results_effects.values() if v) +
        sum(1 for v in results_transitions.values() if v) +
        sum(1 for v in results_styles.values() if v)
    )
    total_tests = (
        len(results_effects) +
        len(results_transitions) +
        len(results_styles)
    )
    
    print(f"Effects:     {sum(1 for v in results_effects.values() if v)}/{len(results_effects)}")
    print(f"Transitions: {sum(1 for v in results_transitions.values() if v)}/{len(results_transitions)}")
    print(f"Styles:      {sum(1 for v in results_styles.values() if v)}/{len(results_styles)}")
    print(f"\nTOTAL:       {total_passed}/{total_tests} PASSED")
    
    print(f"\nAll outputs saved to: {TEST_OUTPUT_DIR}")
    print("Files ready for visual inspection ✓")


if __name__ == "__main__":
    main()
