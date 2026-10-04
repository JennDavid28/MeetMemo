from typing import List, Optional, Dict
from pydantic import BaseModel

class EntityItem(BaseModel):
    text: str
    label: str  # PERSON, ORG, DATE, PROJECT, etc.

class SentimentScore(BaseModel):
    overall: str  # Positive, Negative, Neutral
    positive_pct: float
    negative_pct: float
    neutral_pct: float

class SentimentTimeline(BaseModel):
    timestamp: float
    sentiment: str

class EmotionResult(BaseModel):
    primary_emotion: str
    confidence: float

class IntentItem(BaseModel):
    speaker: str
    text: str
    intent_type: str  # Request, Question, Suggestion, Commitment, Approval

class NLPAnalysisResult(BaseModel):
    entities: List[EntityItem]
    keywords: List[str]
    topics: List[str]
    sentiment: SentimentScore
    sentiment_timeline: List[SentimentTimeline] = []
    emotions: Dict[str, EmotionResult] = {}
    intents: List[IntentItem] = []