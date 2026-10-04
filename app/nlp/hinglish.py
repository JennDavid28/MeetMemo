import re
from typing import List

# Common Hinglish/Hindi words in English script
HINGLISH_KEYWORDS = {
    "ha", "haan", "hai", "hain", "kya", "kyun", "kaise", "kare", "karna", "karo",
    "ho", "hu", "hoon", "thi", "tha", "the", "bhi", "toh", "par", "se", "ko", "ne",
    "ka", "ki", "ke", "sab", "kuch", "aaj", "kal", "abhi", "baad", "pehle", "samajh",
    "baat", "chahiye", "kuchh", "andar", "baahar", "hoga", "hogi", "samajhe"
}

def detect_hinglish_ratio(text: str) -> float:
    """
    Calculates the ratio of Hinglish words present in the given text string.
    Returns a percentage rounded to 2 decimal places (0.0 to 100.0).
    """
    if not text or not text.strip():
        return 0.0

    # Tokenize words ignoring punctuation
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 0.0

    hinglish_count = sum(1 for word in words if word in HINGLISH_KEYWORDS)
    ratio = (hinglish_count / len(words)) * 100.0
    
    return round(ratio, 2)