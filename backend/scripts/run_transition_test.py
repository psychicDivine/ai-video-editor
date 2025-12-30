"""Small helper to run a local transition test using TransitionService.

Usage (from repo root):
  & .venv/Scripts/Activate.ps1
  python backend/scripts/run_transition_test.py

This script will generate two color clips with ffmpeg (if available),
apply a transition using TransitionService, and write an MLT project hint.
"""
import subprocess
import sys
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
OUTDIR = BACKEND / "tmp_test"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Ensure backend is importable when running from repository root
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

def which(cmd):
    return shutil.which(cmd) is not None

def gen_color(path, color, duration=5):
    if not which("ffmpeg"):
        print("ffmpeg not found in PATH; please install ffmpeg to run the test")
        return False
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={color}:s=320x240:d={duration}",
        str(path),
    ]
    subprocess.run(cmd, check=True)
    return True

def main():
    try:
        from app.services.transition_service import TransitionService
        from app.exporters.mlt_exporter import MLTExporter
    except Exception as e:
        print("Failed to import backend helpers; ensure backend is on PYTHONPATH and venv has deps:", e)
        print("If you see 'No module named pydantic_settings' install backend requirements: pip install -r backend/requirements.txt")
        sys.exit(1)

    a = OUTDIR / "red.mp4"
    b = OUTDIR / "blue.mp4"

    print("Generating test clips...")
    gen_color(a, "red")
    gen_color(b, "blue")

    ts = TransitionService(output_dir=str(OUTDIR))
    print("Applying dissolve transition...")
    out = ts.apply_transition(str(a), str(b), duration=1.0, output_name="test_transition.mp4")
    print("Transition output:", out)

    print("Writing MLT project...")
    me = MLTExporter()
    clips = [
        {"path": str(a), "transition": {"type": "dissolve", "duration": 1.0}},
        {"path": str(b), "transition": {"type": "dissolve", "duration": 1.0}},
    ]
    mlt = me.export(clips, str(OUTDIR / "test_project.mlt"))
    print("MLT written:", mlt)

if __name__ == "__main__":
    main()
