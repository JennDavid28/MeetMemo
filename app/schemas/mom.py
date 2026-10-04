from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.action import ActionItem
from app.schemas.decision import Decision, Motion

class MeetingDetails(BaseModel):
    title: str = Field("General Meeting", example="NLP Pipeline Progress")
    date: str = Field("Not specified", example="2026-10-01")
    time: str = Field("Not specified", example="10:00 AM")
    location: str = Field("Not specified", example="Online - Google Meet")
    meeting_type: str = Field("Internal Review", example="Project Review")

class MinutesOfMeeting(BaseModel):
    details: MeetingDetails
    attendance: List[str]
    agenda: List[str]
    executive_summary: str
    discussions: List[str]
    decisions: List[Decision]
    motions: List[Motion] = []
    action_items: List[ActionItem]
    unresolved_questions: List[str]
    next_meeting: Optional[str] = "Not specified"