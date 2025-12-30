import librosa
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class BeatDetector:
    """Detect beats and segment points in audio using Librosa"""

    def __init__(self, sr: int = 22050):
        self.sr = sr

    def detect_beats(self, audio_path: str) -> Tuple[np.ndarray, float]:
        """Detect beat times in audio file
        
        Returns:
            beats: Array of beat times in seconds
            tempo: Estimated tempo in BPM
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr)

            # Compute onset envelope and tempo/beat frames
            hop_length = 512
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
            tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)

            # Convert beat frames to time
            beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=hop_length)

            # Ensure tempo is a float
            if isinstance(tempo, np.ndarray):
                tempo = float(tempo)

            logger.info(f"Detected {len(beat_times)} beats at {tempo:.1f} BPM")
            return beat_times, tempo
        except Exception as e:
            logger.error(f"Error detecting beats: {e}")
            return np.array([]), 0.0

    def get_segment_points(
        self, audio_path: str, segment_duration: float = 30.0
    ) -> List[Tuple[float, float]]:
        """Get optimal segment points based on beats
        
        Args:
            audio_path: Path to audio file
            segment_duration: Duration of segment in seconds
            
        Returns:
            List of (start_time, end_time) tuples for potential segments
        """
        try:
            beat_times, tempo = self.detect_beats(audio_path)
            
            if len(beat_times) == 0:
                logger.warning("No beats detected, using fixed intervals")
                y, sr = librosa.load(audio_path, sr=self.sr)
                duration = librosa.get_duration(y=y, sr=sr)
                return [(0, min(segment_duration, duration))]
            
            # Find segments that start and end on beats
            segments = []
            for i, start_beat in enumerate(beat_times):
                end_beat = start_beat + segment_duration
                
                # Find beat closest to end time
                closest_beat_idx = np.argmin(np.abs(beat_times - end_beat))
                end_time = beat_times[closest_beat_idx]
                
                # Ensure segment is valid
                if end_time - start_beat >= segment_duration * 0.8:  # At least 80% of target
                    segments.append((float(start_beat), float(end_time)))
            
            logger.info(f"Found {len(segments)} potential segments")
            return segments
        except Exception as e:
            logger.error(f"Error getting segment points: {e}")
            return []

    def analyze_energy(self, audio_path: str, segment_start: float, segment_end: float) -> float:
        """Analyze energy level of a segment
        
        Returns:
            Energy score (0-1)
        """
        try:
            y, sr = librosa.load(audio_path, sr=self.sr)
            
            # Convert times to samples
            start_sample = librosa.time_to_samples(segment_start, sr=sr)
            end_sample = librosa.time_to_samples(segment_end, sr=sr)
            
            # Extract segment
            segment = y[start_sample:end_sample]
            
            # Calculate RMS energy
            energy = np.sqrt(np.mean(segment ** 2))
            
            # Normalize to 0-1 range
            normalized_energy = min(1.0, energy / 0.1)
            
            return normalized_energy
        except Exception as e:
            logger.error(f"Error analyzing energy: {e}")
            return 0.5

    def _compute_beat_strengths(self, y: np.ndarray, sr: int, beats_frames: np.ndarray, hop_length: int = 512) -> np.ndarray:
        """Compute a strength score for each beat by sampling the onset envelope around the beat frame."""
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
            strengths = []
            half_window = 2  # frames on either side
            for bf in beats_frames:
                start = max(0, int(bf - half_window))
                end = min(len(onset_env), int(bf + half_window) + 1)
                strengths.append(float(np.max(onset_env[start:end]) if end > start else 0.0))
            strengths = np.array(strengths)
            # normalize
            if strengths.max() > 0:
                strengths = strengths / float(strengths.max())
            return strengths
        except Exception as e:
            logger.error(f"Error computing beat strengths: {e}")
            return np.zeros(len(beats_frames))

    def get_best_segment(
        self, audio_path: str, segment_duration: float = 30.0
    ) -> Tuple[float, float]:
        """Get the best segment based on energy and beat alignment
        
        Returns:
            (start_time, end_time) of best segment
        """
        try:
            segments = self.get_segment_points(audio_path, segment_duration)
            
            if not segments:
                y, sr = librosa.load(audio_path, sr=self.sr)
                duration = librosa.get_duration(y=y, sr=sr)
                return (0.0, min(segment_duration, duration))
            
            # Score segments by energy
            best_segment = segments[0]
            best_score = 0.0
            
            for segment in segments:
                energy = self.analyze_energy(audio_path, segment[0], segment[1])
                if energy > best_score:
                    best_score = energy
                    best_segment = segment
            
            logger.info(f"Best segment: {best_segment[0]:.1f}s - {best_segment[1]:.1f}s (energy: {best_score:.2f})")
            return best_segment
        except Exception as e:
            logger.error(f"Error getting best segment: {e}")
            return (0.0, segment_duration)

    def get_cut_points(
        self, audio_path: str, num_cuts: int = 3
    ) -> List[float]:
        """Get optimal cut points for video segments based on beats
        
        Args:
            audio_path: Path to audio file
            num_cuts: Number of cuts to make
            
        Returns:
            List of cut times in seconds
        """
        try:
            # Load audio and compute beat frames + strengths
            y, sr = librosa.load(audio_path, sr=self.sr)
            hop_length = 512
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
            tempo, beats_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)
            beat_times = librosa.frames_to_time(beats_frames, sr=sr, hop_length=hop_length)

            if len(beat_times) == 0:
                logger.warning("No beats detected for cut points")
                return []

            # Compute beat strengths
            beat_strengths = self._compute_beat_strengths(y, sr, beats_frames, hop_length=hop_length)

            # Candidate beats: prefer strongest beats and enforce minimum spacing
            min_spacing_sec = 2.5
            # Build list of (time, strength)
            candidates = list(zip(beat_times.tolist(), beat_strengths.tolist()))

            # Sort candidates by strength descending
            candidates_sorted = sorted(candidates, key=lambda x: x[1], reverse=True)

            selected = []
            for t, s in candidates_sorted:
                # enforce min spacing
                if any(abs(t - sel) < min_spacing_sec for sel in selected):
                    continue
                selected.append(t)
                if len(selected) >= num_cuts:
                    break

            # If not enough selected, fall back to evenly spaced beats
            if len(selected) < num_cuts:
                indices = np.linspace(0, len(beat_times) - 1, num_cuts + 1, dtype=int)
                selected = beat_times[indices[1:-1]].tolist()

            selected_sorted = sorted(selected)
            logger.info(f"Cut points: {[f'{t:.1f}s' for t in selected_sorted]}")
            return [float(t) for t in selected_sorted]
        except Exception as e:
            logger.error(f"Error getting cut points: {e}")
            return []
