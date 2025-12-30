from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import shutil
from pathlib import Path
import uuid
import json

from app.services.transition_service import TransitionService, TransitionType

router = APIRouter(prefix="/api/transitions", tags=["transitions"])

transition_service = TransitionService()
UPLOAD_DIR = Path("tmp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/available")
async def get_available_transitions():
    try:
        transitions = transition_service.get_all_transitions()
        return {"status": "success", "total_transitions": len(transitions), "transitions": transitions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply")
async def apply_transition(
    video1: UploadFile = File(...),
    video2: UploadFile = File(...),
    transition: str = Form("dissolve"),
    duration: float = Form(1.0),
):
    try:
        try:
            trans_type = TransitionType(transition)
        except Exception:
            raise ValueError(f"Invalid transition: {transition}")

        if duration < 0.5 or duration > 5.0:
            raise ValueError("Duration must be between 0.5 and 5.0 seconds")

        job_id = str(uuid.uuid4())

        video1_path = UPLOAD_DIR / f"{job_id}_video1_{video1.filename}"
        video2_path = UPLOAD_DIR / f"{job_id}_video2_{video2.filename}"

        with open(video1_path, "wb") as f:
            shutil.copyfileobj(video1.file, f)
        with open(video2_path, "wb") as f:
            shutil.copyfileobj(video2.file, f)

        output_path = transition_service.apply_transition(
            video1_path=str(video1_path),
            video2_path=str(video2_path),
            transition=trans_type,
            duration=duration,
            output_name=f"{job_id}_output.mp4",
        )

        return {
            "status": "success",
            "job_id": job_id,
            "transition": transition,
            "duration": duration,
            "output_file": Path(output_path).name,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-multiple")
async def apply_multiple_transitions(videos: List[UploadFile] = File(...), transitions_json: str = Form(...)):
    try:
        transitions = json.loads(transitions_json)
        if len(transitions) != len(videos) - 1:
            raise ValueError(f"Need {len(videos) - 1} transitions for {len(videos)} videos")

        job_id = str(uuid.uuid4())
        video_paths = []
        for i, video in enumerate(videos):
            video_path = UPLOAD_DIR / f"{job_id}_video{i}_{video.filename}"
            with open(video_path, "wb") as f:
                shutil.copyfileobj(video.file, f)
            video_paths.append(str(video_path))

        output_path = transition_service.apply_multiple_transitions(
            video_paths=video_paths, transitions=transitions, output_name=f"{job_id}_multi_output.mp4"
        )

        return {
            "status": "success",
            "job_id": job_id,
            "video_count": len(videos),
            "transition_count": len(transitions),
            "output_file": Path(output_path).name,
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
