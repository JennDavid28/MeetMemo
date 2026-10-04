import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MeetingRecord

router = APIRouter(prefix="/api/mom", tags=["Minutes of Meeting"])

class SaveMoMRequest(BaseModel):
    user_id: str
    title: str
    transcript_text: str
    mom_content: str

@router.post("/save")
def save_mom(request: SaveMoMRequest, db: Session = Depends(get_db)):
    meeting_id = f"meet_{uuid.uuid4().hex[:8]}"
    record = MeetingRecord(
        id=meeting_id,
        user_id=request.user_id,
        title=request.title or "Untitled Meeting",
        original_transcript=request.transcript_text,
        mom_output=request.mom_content
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "success", "meeting_id": meeting_id, "message": "MoM saved successfully."}

@router.get("/user/{user_id}")
def get_user_moms(user_id: str, db: Session = Depends(get_db)):
    try:
        records = db.query(MeetingRecord).filter(MeetingRecord.user_id == user_id).all()
        output = []
        for r in records:
            created_str = r.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(r, 'created_at') and r.created_at else "Recently"
            output.append({
                "id": r.id,
                "title": r.title,
                "created_at": created_str,
                "mom_output": r.mom_output,
                "transcript": r.original_transcript
            })
        return output
    except Exception as e:
        print(f"[Database Error] Failed to query user meetings: {e}")
        return []

@router.delete("/delete/{meeting_id}")
def delete_mom(meeting_id: str, db: Session = Depends(get_db)):
    record = db.query(MeetingRecord).filter(MeetingRecord.id == meeting_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Meeting record not found.")
    db.delete(record)
    db.commit()
    return {"status": "success", "message": "Record deleted."}

@router.post("/export/markdown")
def export_markdown(request: SaveMoMRequest):
    os.makedirs("outputs/mom", exist_ok=True)
    filename = f"outputs/mom/MoM_{uuid.uuid4().hex[:6]}.md"
    
    formatted_doc = f"# {request.title}\n\n" + request.mom_content
    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_doc)
        
    return FileResponse(filename, filename=f"{request.title.replace(' ', '_')}.md", media_type="text/markdown")