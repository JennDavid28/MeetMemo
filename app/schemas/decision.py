from typing import Optional
from pydantic import BaseModel, Field

class Decision(BaseModel):
    decision_text: str = Field(..., example="Use Whisper for speech-to-text.")
    status: str = Field("Confirmed", example="Confirmed")
    context: Optional[str] = Field(None, example="Discussed during model evaluation.")

class Motion(BaseModel):
    motion_text: str = Field(..., example="Use Whisper for transcription.")
    proposed_by: str = Field(..., example="Rahul")
    seconded_by: Optional[str] = Field(None, example="Jennica")
    result: str = Field(..., example="Approved")