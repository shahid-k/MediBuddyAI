"""
bert_score.py   BERTScore (semantic similarity) utility
Requires:  bert-score  and torch  (pip install bert-score torch)
Docs: https://github.com/Tiiiger/bert_score
"""
from bert_score import score
from evaluate import load

# Instantiate once at module import (GPU used if available)
# _scorer = BERTScorer(lang="en",  # adjust if you have multilingual output
#                      rescale_with_baseline=True,
#                      device="cuda" if torch.cuda.is_available() else "cpu")

# bertscore = load("bertscore")

def bert_score(predictions: list[str], references: list[str]) -> list[float]:
    """
    Returns a list of BERTScore F1 scores, one per (pred, ref) pair.
    """
    P, R, F1 = score([predictions], [references], lang="en", model_type="bert-base-uncased")
    return F1.tolist()
