from app.schemas.analysis import SentimentScore

def analyze_sentiment(text: str) -> SentimentScore:
    """
    Lightweight rule/lexicon-based sentiment analysis fallback.
    Can be swapped with HuggingFace transformers pipeline.
    """
    pos_words = {"good", "great", "perfect", "complete", "approved", "completed", "thanks"}
    neg_words = {"remaining", "delay", "issue", "bug", "failed", "pending", "problem"}
    
    words = text.lower().split()
    pos_count = sum(1 for w in words if w in pos_words)
    neg_count = sum(1 for w in words if w in neg_words)
    total = len(words) or 1

    pos_pct = round((pos_count / total) * 100, 1)
    neg_pct = round((neg_count / total) * 100, 1)
    neu_pct = round(100.0 - (pos_pct + neg_pct), 1)

    overall = "Neutral"
    if pos_pct > neg_pct and pos_pct > 10:
        overall = "Positive"
    elif neg_pct > pos_pct and neg_pct > 10:
        overall = "Negative"

    return SentimentScore(
        overall=overall,
        positive_pct=pos_pct,
        negative_pct=neg_pct,
        neutral_pct=neu_pct
    )