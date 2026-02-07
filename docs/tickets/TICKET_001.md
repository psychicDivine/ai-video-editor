# TICKET_001: TikTok Caption Style Preset

## Metadata
- **Type**: Feature
- **Priority**: P1 (High)
- **Sprint**: SPRINT_001
- **Estimated Hours**: 8
- **Skills Required**: Python, FFmpeg, TypeScript

---

## Description

Implement a TikTok-style caption preset that creates glamorous, attention-grabbing captions with:
- Bold, centered text
- Gradient background highlighting current word
- Bounce/pop animation on word appearance
- High contrast colors for readability

This will be the first of several caption style presets (TikTok, Hormozi, Neon, Minimal).

---

## Acceptance Criteria

- [ ] Caption service accepts a `style` parameter with value `tiktok`
- [ ] TikTok style produces ASS subtitles with characteristic styling
- [ ] Words animate/pop when spoken (timing from Whisper)
- [ ] Current word has gradient highlight
- [ ] Frontend shows preview of caption style
- [ ] API documentation updated
- [ ] Unit tests cover new style parameter

---

## Technical Approach

### Backend Changes

1. **Update `CaptionService`** (`backend/app/services/caption_service.py`)
   - Add `CaptionStyle` enum: `tiktok`, `hormozi`, `neon`, `minimal`
   - Create `_generate_tiktok_ass()` method
   - ASS styling with `\an5` (centered), `\b1` (bold), `\fscx120\fscy120` (pop effect)

2. **Update API** (`backend/app/routes/youtube.py`)
   - Add `caption_style` to request schema
   - Pass to video processor

### Frontend Changes

1. **Style Selector Component** (`frontend/src/components/CaptionStyleSelector.tsx`)
   - Visual cards showing style preview
   - Updates parent state with selected style

2. **Update Upload Form**
   - Include style in API request

### ASS Styling Reference

```ass
[Script Info]
Title: TikTok Style Captions
ScriptType: v4.00+

[V4+ Styles]
Style: TikTok,Outfit,48,&HFFFFFF,&H000000,&HFF00FF,&H000000,1,0,0,0,100,100,0,0,1,2,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:02.00,TikTok,,0,0,0,,{\fad(100,100)\t(0,100,\fscx110\fscy110)\t(100,200,\fscx100\fscy100)}Hello World
```

---

## Tasks

- [ ] TASK_001_001: Research TikTok caption styling
- [ ] TASK_001_002: Create ASS template for TikTok style
- [ ] TASK_001_003: Add style parameter to caption service
- [ ] TASK_001_004: Create frontend style selector
- [ ] TASK_001_005: Write unit tests

---

## Testing Requirements

### Unit Tests
- `test_caption_style_enum()` - Verify enum values
- `test_tiktok_ass_generation()` - Verify ASS output format
- `test_style_parameter_passed()` - API passes style correctly

### Integration Tests
- Full flow: YouTube URL → Processing → TikTok-styled captions

### Manual Verification
1. Process a video with TikTok style
2. Play result and verify captions animate correctly
3. Check readability on both light and dark video content

---

## Dependencies

- Depends on: None (standalone feature)
- Blocks: TICKET_002 (Post-Preview Editor needs style system)

---

## Observations (Updated by Executor)

### Implementation Notes
*[To be filled during execution]*

### Blockers Encountered
*[To be filled during execution]*

### Suggested Improvements
*[To be filled during execution]*
