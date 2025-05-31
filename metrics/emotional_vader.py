"""
emotional_vader.py  – VADER sentiment / “emotional depth” utility
Requires:  nltk   (pip install nltk)
On first import the VADER lexicon is downloaded.
"""
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# One-time download (silenced)
nltk.download("vader_lexicon", quiet=True)

_sia = SentimentIntensityAnalyzer()


def vader_scores(text: str) -> dict[str, float]:
    """
    Returns VADER polarity scores:
    {neg, neu, pos, compound}.  Higher |compound| indicates stronger emotion.
    """
    return _sia.polarity_scores(text)
