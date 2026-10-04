import re
from app.schemas.transcript import LanguageAnalysis

# Common Hindi keywords in Roman script (Hinglish)
HINGLISH_KEYWORDS = {
    "hai", "hein", "ho", "haan", "nahin", "nahi", "kar", "karna", "raha", 
    "rahi", "karo", "kya", "kaise", "kal", "aaj", "baaki", "hogaya", "thik"
}

def detect_language(text: str) -> LanguageAnalysis:
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return LanguageAnalysis(detected_language="English", english_ratio=1.0, hindi_ratio=0.0, code_switching=False)

    hindi_count = sum(1 for w in words if w in HINGLISH_KEYWORDS)
    total_words = len(words)
    
    hindi_ratio = round(hindi_count / total_words, 2)
    english_ratio = round(1.0 - hindi_ratio, 2)
    
    is_hinglish = hindi_count > 0 and english_ratio > 0.2
    detected = "Hinglish" if is_hinglish else "English"
    
    return LanguageAnalysis(
        detected_language=detected,
        english_ratio=english_ratio,
        hindi_ratio=hindi_ratio,
        code_switching=is_hinglish
    )