import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

from app.nlp.ner import extract_entities
from app.nlp.keywords import extract_keywords
from app.nlp.sentiment import analyze_sentiment
from app.nlp.hinglish import detect_hinglish_ratio

@dataclass
class EntityItem:
    text: str
    label: str

@dataclass
class NLPResults:
    entities: List[EntityItem] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    sentiment: Dict[str, Any] = field(default_factory=dict)
    participation: List[Dict[str, Any]] = field(default_factory=list)
    hinglish_ratio: float = 0.0

def run_nlp_pipeline(transcript) -> NLPResults:
    text = transcript.full_original_text if hasattr(transcript, "full_original_text") else str(transcript)
    utterances = transcript.utterances if hasattr(transcript, "utterances") else []

    # 1. DYNAMIC ACTION ITEM EXTRACTION FROM TRANSCRIPT UTTERANCES
    action_triggers = [
        "will", "need to", "going to", "action", "circulate", "send", "review", 
        "deliver", "look into", "get back", "assign", "prepare", "complete", "submit"
    ]
    extracted_actions = []
    
    if utterances:
        for utt in utterances:
            utt_text = utt.text if hasattr(utt, "text") else str(utt)
            speaker = utt.speaker if hasattr(utt, "speaker") else "Participant"
            if any(re.search(r'\b' + re.escape(trig) + r'\b', utt_text, re.IGNORECASE) for trig in action_triggers):
                if len(utt_text.strip()) > 10:
                    extracted_actions.append(f"{speaker}: {utt_text.strip()}")
    else:
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if any(re.search(r'\b' + re.escape(trig) + r'\b', sentence, re.IGNORECASE) for trig in action_triggers):
                if len(sentence.strip()) > 10:
                    extracted_actions.append(sentence.strip())

    # 2. DYNAMIC KEYWORD EXTRACTION (TF-IDF via sklearn)
    dynamic_keywords = extract_keywords(text, top_n=10)

    # 3. DYNAMIC ENTITY EXTRACTION (SpaCy NER)
    raw_entities = extract_entities(text)
    entities = [EntityItem(text=getattr(e, 'text', str(e)), label=getattr(e, 'label', 'ENTITY')) for e in raw_entities]

    # 4. SPEAKER PARTICIPATION SHARE COMPUTATION
    speaker_lengths = {}
    total_chars = 0
    for utt in utterances:
        speaker = getattr(utt, "speaker", "Speaker 1")
        text_len = len(getattr(utt, "text", ""))
        speaker_lengths[speaker] = speaker_lengths.get(speaker, 0) + text_len
        total_chars += text_len

    participation = []
    if total_chars > 0:
        for speaker, length in speaker_lengths.items():
            pct = round((length / total_chars) * 100, 1)
            participation.append({"speaker": speaker, "percentage": pct})
    else:
        participation = [{"speaker": "Speaker 1", "percentage": 100.0}]

    # 5. DYNAMIC SENTIMENT & HINGLISH RATIO
    sentiment_result = analyze_sentiment(text)
    sentiment_dict = {
        "vibe": getattr(sentiment_result, "overall", "Neutral"),
        "positive": getattr(sentiment_result, "positive_pct", 0.0),
        "negative": getattr(sentiment_result, "negative_pct", 0.0),
        "neutral": getattr(sentiment_result, "neutral_pct", 100.0)
    }
    hinglish_pct = detect_hinglish_ratio(text)

    return NLPResults(
        entities=entities,
        keywords=dynamic_keywords,
        action_items=extracted_actions[:8],
        sentiment=sentiment_dict,
        participation=participation,
        hinglish_ratio=hinglish_pct
    )