from typing import List, Optional
from pydantic import BaseModel, Field

class Utterance(BaseModel):
    speaker: str = Field(..., json_schema_extra={"example": "Speaker 1"})
    text: str = Field(..., json_schema_extra={"example": "Good morning everyone."})
    start_time: Optional[float] = Field(None, json_schema_extra={"example": 0.0})
    end_time: Optional[float] = Field(None, json_schema_extra={"example": 5.4})
    translated_text: Optional[str] = Field(None, json_schema_extra={"example": "Good morning everyone."})

class LanguageAnalysis(BaseModel):
    detected_language: str = Field(..., json_schema_extra={"example": "Hinglish"})
    english_ratio: float = Field(..., json_schema_extra={"example": 0.65})
    hindi_ratio: float = Field(..., json_schema_extra={"example": 0.35})
    code_switching: bool = Field(..., json_schema_extra={"example": True})

class UnifiedTranscript(BaseModel):
    meeting_id: Optional[str] = Field(None, json_schema_extra={"example": "meet_12345"})
    utterances: List[Utterance]
    full_original_text: str
    full_translated_text: Optional[str] = None
    language_info: Optional[LanguageAnalysis] = None