import re
from app.schemas.transcript import LanguageAnalysis

# Common Hindi keywords in Roman script (excluding common English words like 'ho', 'kar')
HINGLISH_KEYWORDS = {
    "hai", "hain", "haan", "nahin", "nahi", "karna", "raha", 
    "rahi", "karo", "kya", "kaise", "kal", "aaj", "baaki", "hogaya", "thik",
    "karenge", "accha", "achha", "bahut", "bohot", "lekin", "mera", "meri"
}

ENGLISH_EXCLUSIONS = {
    "the", "to", "in", "is", "it", "of", "and", "a", "an", "on", "for", "with",
    "as", "at", "by", "from", "up", "about", "into", "over", "after", "ha", "par",
    "so", "no", "or", "be", "do", "we", "he", "she", "me", "my", "us", "if", "all"
}

def detect_language(text: str) -> LanguageAnalysis:
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return LanguageAnalysis(detected_language="English", english_ratio=1.0, hindi_ratio=0.0, code_switching=False)

    genuine_hindi = [w for w in words if w in HINGLISH_KEYWORDS and w not in ENGLISH_EXCLUSIONS]
    hindi_count = len(genuine_hindi)
    total_words = len(words)
    
    hindi_ratio = round(hindi_count / total_words, 2)
    english_ratio = round(1.0 - hindi_ratio, 2)
    
    # Require at least 5% Hindi and multiple markers to classify as Hinglish code-switching
    is_hinglish = hindi_ratio >= 0.05 and hindi_count >= 2
    detected = "Hinglish" if is_hinglish else "English"
    
    return LanguageAnalysis(
        detected_language=detected,
        english_ratio=english_ratio,
        hindi_ratio=hindi_ratio,
        code_switching=is_hinglish
    )