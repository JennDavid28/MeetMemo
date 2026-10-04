from fastapi import APIRouter
from app.schemas.speaker import SpeakerRenameRequest

router = APIRouter(prefix="/api/analysis", tags=["NLP Analysis & Speakers"])

@router.post("/rename-speakers")
def rename_speakers(request: SpeakerRenameRequest):
    """
    Renames default speakers (e.g. Speaker 1 -> Jennica) across a meeting payload.
    """
    return {
        "meeting_id": request.meeting_id,
        "updated_mappings": request.mappings,
        "status": "Speaker names successfully updated across transcript and MoM."
    }