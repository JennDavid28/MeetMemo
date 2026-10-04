from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SpeakerSegment(BaseModel):
    speaker_id: str = Field(..., json_schema_extra={"example": "Speaker 1"})
    start: float = Field(..., json_schema_extra={"example": 0.0})
    end: float = Field(..., json_schema_extra={"example": 5.4})

class SpeakerRenameRequest(BaseModel):
    meeting_id: str
    mappings: Dict[str, str] = Field(..., json_schema_extra={"example": {"Speaker 1": "Jennica", "Speaker 2": "Rahul"}})

class SpeakerStats(BaseModel):
    speaker_name: str
    speaking_time_seconds: float
    speaking_percentage: float
    word_count: int