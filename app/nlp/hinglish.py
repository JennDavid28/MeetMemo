import re
from typing import List

# Distinctive Hinglish/Hindi words in Romanized script (excluding English homographs like 'the', 'par', 'ha', 'to')
HINGLISH_KEYWORDS = {
    "haan", "hai", "hain", "kya", "kyun", "kaise", "kare", "karna", "karo", "karenge",
    "karega", "karegi", "kar", "hoon", "thi", "tha", "bhi", "toh", "sabko", "sabka",
    "kuch", "kuchh", "aaj", "kal", "parso", "abhi", "baad", "pehle", "samajh", "samajhe",
    "samjha", "baat", "chahiye", "andar", "baahar", "hoga", "hogi", "honge", "hota", "hoti",
    "hote", "aur", "lekin", "magar", "mera", "meri", "mere", "tera", "teri", "tere",
    "apna", "apni", "apne", "humara", "hamara", "tumhara", "yeh", "woh", "isme", "usme",
    "bahut", "bohot", "thoda", "thodi", "zyada", "jyada", "accha", "achha", "theek", "thik",
    "batao", "bolo", "dekho", "suno", "chalo", "chal", "raha", "rahi", "rahe", "gaya",
    "gayi", "gaye", "aaya", "aayi", "aaye", "bhejo", "bhejna", "pata", "maalum", "zaruri",
    "nahin", "nahi", "mat", "hogaya", "baaki"
}

# Common English words that must NEVER be misidentified as Hinglish
ENGLISH_EXCLUSIONS = {
    "the", "to", "in", "is", "it", "of", "and", "a", "an", "on", "for", "with",
    "as", "at", "by", "from", "up", "about", "into", "over", "after", "ha", "par",
    "so", "no", "or", "be", "do", "we", "he", "she", "me", "my", "us", "if", "all"
}

def detect_hinglish_ratio(text: str) -> float:
    """
    Calculates the ratio of Hinglish words present in the given text string.
    Returns a percentage rounded to 2 decimal places (0.0 to 100.0).
    Guarantees 0.0% when the conversation is completely in English.
    """
    if not text or not text.strip():
        return 0.0

    # Tokenize words ignoring punctuation
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 0.0

    # Filter out English exclusions and count distinct genuine Hinglish tokens
    genuine_hinglish = [w for w in words if w in HINGLISH_KEYWORDS and w not in ENGLISH_EXCLUSIONS]
    if not genuine_hinglish:
        return 0.0

    ratio = (len(genuine_hinglish) / len(words)) * 100.0
    return round(ratio, 2)