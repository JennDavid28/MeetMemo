import os
import shutil
import uuid
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.pipeline.audio_pipeline import run_audio_pipeline

router = APIRouter(prefix="/api/audio", tags=["Audio Input Mode"])

SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".flac", ".mp4", ".m4b", ".webm", ".ogg", ".aac"}

@router.post("/upload")
async def upload_audio_file(file: UploadFile = File(...)):
    if not file.filename:
        file.filename = "audio_input.webm"
        
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext or ext not in SUPPORTED_FORMATS:
        ext = ".webm"  # Default browser audio format
    
    temp_id = uuid.uuid4().hex[:8]
    temp_path = f"outputs/transcripts/upload_{temp_id}{ext}"
    
    os.makedirs("outputs/transcripts", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        results = await run_in_threadpool(run_audio_pipeline, temp_path)
        return results
    except Exception as e:
        print("\n" + "="*50)
        print("Detailed Audio Pipeline Crash Traceback:")
        traceback.print_exc()
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@router.post("/record")
async def process_recorded_audio(file: UploadFile = File(...)):
    """Handles direct browser microphone recordings from recorder.js."""
    return await upload_audio_file(file)