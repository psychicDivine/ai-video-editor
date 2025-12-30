import numpy as np
from typing import List, Tuple
from .beat_detector import BeatDetector
import logging

logger = logging.getLogger(__name__)


class SegmentPlanner:
    """Plan segments using beat information, preferring downbeats/strong beats and enforcing minimum spacing."""

    def __init__(self, beats_per_bar: int = 4, min_segment_sec: float = 3.0, min_spacing_sec: float = 2.5):
        self.beats_per_bar = beats_per_bar
        self.min_segment_sec = min_segment_sec
        self.min_spacing_sec = min_spacing_sec
        self.detector = BeatDetector()

    def plan_segments(self, audio_path: str, num_segments: int = 3, segment_duration: float = 30.0) -> List[Tuple[float, float]]:
        """Return list of (start, end) tuples for segments sized to approximately segment_duration/num_segments, aligned to strong beats/downbeats."""
        try:
            beat_times, tempo = self.detector.detect_beats(audio_path)
            if len(beat_times) == 0:
                logger.warning("No beats detected in SegmentPlanner, falling back to fixed segments")
                return [(i * (segment_duration / num_segments), (i + 1) * (segment_duration / num_segments)) for i in range(num_segments)]

            # Compute target segment length
            target_len = segment_duration / float(num_segments)

            # For each bar, pick strongest beat (approx every beats_per_bar beats)
            candidates = []
            # Ensure we have indices
            for i in range(0, len(beat_times), max(1, self.beats_per_bar)):
                # window to examine within a bar
                window = beat_times[i:i + self.beats_per_bar]
                if len(window) == 0:
                    continue
                # choose the first beat as downbeat candidate
                candidates.append(window[0])

            # Now pick segment centers greedily spaced by target_len, snapping to nearest candidate
            segments = []
            used = []
            for seg_idx in range(num_segments):
                desired_center = (seg_idx + 0.5) * target_len
                # find candidate closest to desired_center and respecting min spacing
                best = None
                best_dist = float('inf')
                for c in candidates:
                    if any(abs(c - u) < self.min_spacing_sec for u in used):
                        continue
                    dist = abs(c - desired_center)
                    if dist < best_dist:
                        best_dist = dist
                        best = c
                if best is None:
                    # fallback: use desired_center clipped
                    start = max(0.0, desired_center - target_len / 2.0)
                    end = start + target_len
                else:
                    start = max(0.0, best - target_len / 2.0)
                    end = start + target_len
                    used.append(best)
                segments.append((float(start), float(end)))

            logger.info(f"Planned {len(segments)} segments using {len(candidates)} candidates")
            return segments
        except Exception as e:
            logger.error(f"Error planning segments: {e}")
            return []
