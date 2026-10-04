from typing import List
from app.nlp.preprocessing import segment_sentences

def extract_unresolved_questions(text: str) -> List[str]:
    sentences = segment_sentences(text)
    questions = [s for s in sentences if s.endswith("?")]
    return questions