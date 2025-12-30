from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil
import uuid

from app.services.frei0r_service import FREI0R_PRESETS, apply_frei0r_filter, is_frei0r_available

router = APIRouter(prefix="/api/frei0r", tags=["frei0r"])

UPLOAD_DIR = Path("tmp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/available")
async def frei0r_available():
    try:
        presets = {k: v for k, v in FREI0R_PRESETS.items()}
        available = is_frei0r_available()
        return {"status": "success", "available": available, "presets": presets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply")
async def apply_preset(preset: str = Form(...), file: UploadFile = File(...)):
    try:
        if preset not in FREI0R_PRESETS:
            raise ValueError(f"Unknown preset: {preset}")

        if not is_frei0r_available():
            raise HTTPException(status_code=400, detail="frei0r not available on server FFmpeg build")

        job_id = str(uuid.uuid4())
        in_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        out_path = UPLOAD_DIR / f"{job_id}_frei0r_out_{file.filename}"

        with open(in_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        preset_cfg = FREI0R_PRESETS[preset]
        filter_name = preset_cfg.get("filter")
        params = preset_cfg.get("params")

        ok = apply_frei0r_filter(str(in_path), str(out_path), filter_name, params)
        if not ok:
            raise Exception("Failed to apply frei0r filter via ffmpeg")

        return {"status": "success", "output_file": out_path.name}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
