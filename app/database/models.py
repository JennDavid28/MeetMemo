from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class UserProfile(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="Participant")
    created_at = Column(DateTime, default=datetime.utcnow)

    meetings = relationship("MeetingRecord", back_populates="user")


class MeetingRecord(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String, default="General Meeting")
    original_transcript = Column(Text, nullable=False)
    translated_transcript = Column(Text, nullable=True)
    language_info = Column(Text, nullable=True)
    nlp_results = Column(Text, nullable=True)
    mom_output = Column(Text, nullable=True)

    user = relationship("UserProfile", back_populates="meetings")