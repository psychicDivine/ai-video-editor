from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import subprocess
import wave
import audioop
import math
import logging

router = APIRouter(prefix="/api", tags=["audio"])

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("tmp_audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/analyze-beats")
async def analyze_beats(audio: UploadFile = File(...), start: float | None = None, end: float | None = None):
    """Simple beat analysis endpoint.

    Saves the uploaded file, converts to mono WAV via ffmpeg, computes
    short-time energy peaks and returns `beats` (timestamps) and
    `proposedCuts` (timestamps + confidence).
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    uid = str(uuid.uuid4())
    src_path = UPLOAD_DIR / f"{uid}_{audio.filename}"
    wav_path = UPLOAD_DIR / f"{uid}.wav"

    try:
        contents = await audio.read()
        with open(src_path, "wb") as f:
            f.write(contents)

        # Convert to mono 22050 Hz WAV using ffmpeg
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(src_path),
            "-ar",
            "22050",
            "-ac",
            "1",
            "-f",
            "wav",
            str(wav_path),
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            logger.error(f"ffmpeg failed: {proc.stderr}")
            raise HTTPException(status_code=500, detail="Failed to decode audio (ffmpeg error)")

        # Read wav and compute short-time energy
        with wave.open(str(wav_path), "rb") as wf:
            nchannels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            nframes = wf.getnframes()

            window_ms = 40
            window_size = int(framerate * (window_ms / 1000.0))
            energies = []
            times = []
            total_read = 0
            while total_read < nframes:
                frames = wf.readframes(window_size)
                if not frames:
                    break
                rms = audioop.rms(frames, sampwidth)
                energies.append(rms)
                times.append(total_read / framerate)
                total_read += window_size

        if not energies:
            return JSONResponse(status_code=200, content={"beats": [], "proposedCuts": []})

        # Compute dynamic threshold
        mean_e = sum(energies) / len(energies)
        var = sum((e - mean_e) ** 2 for e in energies) / len(energies)
        std = math.sqrt(var)
        threshold = mean_e + std * 0.8

        # find local peaks above threshold
        beats = []
        for i in range(1, len(energies) - 1):
            if energies[i] > threshold and energies[i] > energies[i - 1] and energies[i] >= energies[i + 1]:
                beats.append(times[i])

        # reduce too-dense peaks: keep peaks separated by at least 0.2s
        filtered = []
        min_sep = 0.2
        for b in beats:
            if not filtered or b - filtered[-1] >= min_sep:
                filtered.append(b)

        # propose cuts at beats with confidence normalized
        max_e = max(energies) or 1
        proposed = []
        for b in filtered:
            # find corresponding energy index
            idx = int((b / (times[-1] + 1e-6)) * len(energies))
            idx = max(0, min(len(energies) - 1, idx))
            conf = min(1.0, energies[idx] / max_e)
            proposed.append({"time": round(b, 3), "confidence": round(conf, 3)})

        # If region params provided, filter beats and proposed to that region
        if start is not None or end is not None:
            s = start if start is not None else 0.0
            e = end if end is not None else times[-1] if times else 0.0
            filtered = [b for b in filtered if b >= s and b <= e]
            proposed = [p for p in proposed if p["time"] >= s and p["time"] <= e]

        return JSONResponse(status_code=200, content={"beats": [round(b, 3) for b in filtered], "proposedCuts": proposed})

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("analyze_beats failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup source file (keep wav for debugging)
        try:
            if src_path.exists():
                src_path.unlink()
        except Exception:
            pass
