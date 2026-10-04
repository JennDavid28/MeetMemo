import json
from sqlalchemy.orm import Session
from app.database.models import MeetingRecord

def save_meeting(db: Session, meeting_id: str, title: str, original_text: str, translated_text: str, lang_info: dict, nlp_data: dict, mom_text: str):
    record = MeetingRecord(
        id=meeting_id,
        title=title,
        original_transcript=original_text,
        translated_transcript=translated_text,
        language_info=json.dumps(lang_info),
        nlp_results=json.dumps(nlp_data),
        mom_output=mom_text
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_meeting_by_id(db: Session, meeting_id: str):
    return db.query(MeetingRecord).filter(MeetingRecord.id == meeting_id).first()