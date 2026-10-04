import spacy
from typing import List
from app.schemas.analysis import EntityItem

_nlp = None

# Entity labels relevant to meeting intelligence
RELEVANT_LABELS = {
    "PERSON",       # People (e.g., Rahul, Jennica)
    "ORG",          # Companies/Organizations (e.g., MUJ, OpenAI, Google)
    "GPE",          # Geopolitical Entities / Locations (e.g., India, Delhi, Office)
    "DATE",         # Dates / Deadlines (e.g., Friday, Next Month)
    "TIME",         # Specific Times (e.g., 10:00 AM)
    "PRODUCT",      # Products / Technologies (e.g., Whisper, FastAPI)
    "WORK_OF_ART"   # Projects / Documents
}

def get_nlp_model():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = None
    return _nlp

def extract_entities(text: str) -> List[EntityItem]:
    if not text or not text.strip():
        return []
    
    nlp = get_nlp_model()
    if not nlp:
        return []
        
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        # Filter out numbers (CARDINAL), ORDINAL, and Speaker label artifacts
        if ent.label_ in RELEVANT_LABELS and ent.text.strip().lower() not in {"speaker 1", "speaker 2", "speaker 3"}:
            entities.append(EntityItem(text=ent.text, label=ent.label_))
            
    return entities