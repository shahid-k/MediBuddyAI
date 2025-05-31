"""
readability.py  - Flesch Reading-Ease utility
Requires:  textstat  (pip install textstat)
"""
from textstat import textstat


def flesch_reading_ease(text: str) -> float:
    """
    Return the Flesch Reading-Ease score.
    90-100 = very easy, 0-30 = very difficult.
    """
    return textstat.flesch_reading_ease(text)

