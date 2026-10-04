from typing import List
from app.schemas.transcript import Utterance

def extract_attendance(utterances: List[Utterance]) -> List[str]:
    speakers = list({u.speaker for u in utterances if u.speaker})
    return sorted(speakers) if speakers else ["Not specified"]