"""Simple diagnostics runner for beat detector and cut point selection.
Writes CSV summaries to test_output/beat_diagnostics/ for tuning.
"""
import os
import csv
from pathlib import Path
from app.services.beat_detector import BeatDetector


def run(audio_paths, out_dir="test_output/beat_diagnostics"):
    os.makedirs(out_dir, exist_ok=True)
    detector = BeatDetector()
    rows = []
    for p in audio_paths:
        print(f"Processing: {p}")
        beats, tempo = detector.detect_beats(p)
        cut_points = detector.get_cut_points(p, num_cuts=3)
        rows.append({
            "file": p,
            "tempo": tempo,
            "num_beats": len(beats),
            "cut_points": ";".join([f"{t:.3f}" for t in cut_points])
        })

    csv_path = Path(out_dir) / "diagnostics.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "tempo", "num_beats", "cut_points"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Diagnostics written to {csv_path}")


if __name__ == "__main__":
    # Example usage: place sample audio in backend/tests/beat_diagnostics/samples/
    samples_dir = Path(__file__).parent / "samples"
    audio_files = []
    if samples_dir.exists():
        for f in samples_dir.iterdir():
            if f.suffix.lower() in {".wav", ".mp3", ".m4a"}:
                audio_files.append(str(f))
    if not audio_files:
        print("No sample audio found in backend/tests/beat_diagnostics/samples/. Add files to run diagnostics.")
    else:
        run(audio_files)
