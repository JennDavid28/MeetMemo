from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    if not text.strip():
        return []
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
        vectorizer.fit_transform([text])
        return list(vectorizer.get_feature_names_out())
    except Exception:
        # Fallback simple frequency count
        words = [w.lower() for w in text.split() if len(w) > 4]
        return list(set(words))[:top_n]