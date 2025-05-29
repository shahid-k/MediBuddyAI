from rouge_score import rouge_scorer

def rouge(predictions: list[str], references: list[str]) -> dict[str, dict[str, float]]:
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    total_scores = {
        'rouge1': {'precision': 0.0, 'recall': 0.0, 'f1': 0.0},
        'rouge2': {'precision': 0.0, 'recall': 0.0, 'f1': 0.0},
        'rougeL': {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    }

    n = len(predictions)

    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        for metric in total_scores:
            total_scores[metric]['precision'] += scores[metric].precision
            total_scores[metric]['recall']    += scores[metric].recall
            total_scores[metric]['f1']        += scores[metric].fmeasure

    # Average scores over all prediction-reference pairs
    for metric in total_scores:
        for score_type in total_scores[metric]:
            total_scores[metric][score_type] /= n

    return total_scores
