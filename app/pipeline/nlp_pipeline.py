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
    action_patterns = [
        r'\b(?:will|can|shall|going to)\s+(?:handle|add|improve|finish|prepare|validate|move|create|update|implement|fix|test|run|experiment|prioritize)\b',
        r'\b(?:should have|have the .* ready|ready by|deadline|action item|task assignment)\b',
        r'\b(?:need to|have to|must)\s+(?:complete|finalize|deliver|deploy|configure|filter)\b'
    ]
    greeting_pattern = r'^(?:good morning|good afternoon|hello|hi|thanks|perfect|great|let\'s start|today i want)\b'
    
    extracted_actions = []
    seen_actions = set()

    if utterances:
        for utt in utterances:
            utt_text = utt.text if hasattr(utt, "text") else str(utt)
            speaker = utt.speaker if hasattr(utt, "speaker") else "Participant"
            # Split utterance into distinct sentences
            sentences = re.split(r'(?<=[.!?])\s+', utt_text)
            for s in sentences:
                s_clean = s.strip()
                if not s_clean or len(s_clean) < 15 or s_clean.endswith('?'):
                    continue
                # Skip greetings and general meeting opening phrases
                if re.search(greeting_pattern, s_clean, re.IGNORECASE):
                    continue
                if any(re.search(pat, s_clean, re.IGNORECASE) for pat in action_patterns):
                    item = f"{speaker}: {s_clean}"
                    if item not in seen_actions:
                        seen_actions.add(item)
                        extracted_actions.append(item)
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences:
            s_clean = s.strip()
            if not s_clean or len(s_clean) < 15 or s_clean.endswith('?'):
                continue
            if re.search(greeting_pattern, s_clean, re.IGNORECASE):
                continue
            if any(re.search(pat, s_clean, re.IGNORECASE) for pat in action_patterns):
                if s_clean not in seen_actions:
                    seen_actions.add(s_clean)
                    extracted_actions.append(s_clean)

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