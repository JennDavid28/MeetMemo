import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MeetingRecord
from app.llm.client import call_llm, load_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa", tags=["Grounded Q&A"])


class QARequest(BaseModel):
    user_id: Optional[str] = None
    transcript_text: Optional[str] = Field(default="", alias="transcript")
    question: str

    class Config:
        populate_by_name = True


@router.post("/ask")
def ask_question(payload: QARequest, db: Session = Depends(get_db)):
    """
    Answers user questions strictly grounded in the active transcript
    AND all historically saved meetings found in SQLite for the user.
    """
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    context_blocks = []

    # 1. Include Active Workspace Context
    active_text = (payload.transcript_text or "").strip()
    if active_text:
        context_blocks.append(f"Meeting Name: Active Meeting Workspace\nContent:\n{active_text}")

    # 2. Include Historical Saved Meetings
    if payload.user_id:
        try:
            records = db.query(MeetingRecord).filter(MeetingRecord.user_id == payload.user_id).all()
            for idx, rec in enumerate(records, 1):
                title = rec.title or f"Meeting #{idx}"
                date_str = rec.created_at.strftime("%Y-%m-%d") if rec.created_at else "Unknown Date"
                content = rec.mom_output or rec.original_transcript or ""
                if content.strip():
                    context_blocks.append(f"Meeting Name: {title}\nDate: {date_str}\nContent:\n{content.strip()}")
        except Exception as e:
            logger.warning(f"Could not query historical meetings: {e}")

    if not context_blocks:
        raise HTTPException(
            status_code=400, 
            detail="No transcript context or saved meetings found to answer your question."
        )

    combined_context = "\n\n====================\n\n".join(context_blocks)

    prompt_content = (
        "You are MeetMemo AI, an assistant for meeting transcripts and saved Minutes of Meetings (MoM).\n"
        "Use the provided Knowledge Base below to answer the user's question directly and concisely.\n"
        "If asked about a specific meeting, summarize its key discussion points and action items.\n"
        "If the information is missing across all files, state 'Information not found in your saved or active meetings.'\n\n"
        f"--- KNOWLEDGE BASE ---\n\n{combined_context}\n\n"
        f"User Question: {question}\n\n"
        "Answer:"
    )

    try:
        answer = call_llm(prompt_content, temperature=0.1)
        if not answer or not answer.strip():
            answer = "Not mentioned in any active or saved meetings."
        return {"status": "success", "question": question, "answer": answer}
    except Exception as err:
        logger.warning(f"LLM execution unavailable ({err}). Running NLP contextual search fallback.")
        q_words = [w.lower() for w in question.split() if len(w) > 3]
        matches = []
        for block in context_blocks:
            for line in block.split("\n"):
                if any(w in line.lower() for w in q_words):
                    matches.append(line.strip())
        if matches:
            fallback_ans = "Based on meeting notes:\n" + "\n".join(set(matches[:4]))
        else:
            fallback_ans = "Information not explicitly found in active meeting notes."
        return {"status": "success", "question": question, "answer": fallback_ans}