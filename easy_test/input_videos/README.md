
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
