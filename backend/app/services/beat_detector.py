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
            
            # Estimate tempo and beat frames
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            
            # Convert beat frames to time
            beat_times = librosa.frames_to_time(beats, sr=sr)
            
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
            beat_times, _ = self.detect_beats(audio_path)
            
            if len(beat_times) < num_cuts:
                logger.warning(f"Not enough beats for {num_cuts} cuts")
                return beat_times.tolist()
            
            # Get evenly spaced beats
            indices = np.linspace(0, len(beat_times) - 1, num_cuts + 1, dtype=int)
            cut_points = beat_times[indices[1:-1]].tolist()
            
            logger.info(f"Cut points: {[f'{t:.1f}s' for t in cut_points]}")
            return cut_points
        except Exception as e:
            logger.error(f"Error getting cut points: {e}")
            return []
