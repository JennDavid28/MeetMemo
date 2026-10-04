from typing import Optional
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    task: str = Field(..., example="Test the transcription model")
    owner: str = Field(..., example="Rahul")
    deadline: Optional[str] = Field("Not specified", example="Friday")
    status: str = Field("Pending", example="Pending")