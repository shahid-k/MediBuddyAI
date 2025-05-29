from evaluate import load

_perplexity_metric = None

def perplexities(texts: list[str], model_id: str = "gpt2") -> list[float]:
    """
    Compute token-level perplexities for a list of texts using the
    specified language-model weights (default: GPT-2).
    """
    global _perplexity_metric
    if _perplexity_metric is None:
        _perplexity_metric = load("perplexity", module_type="metric")

    _perplexity_metric.add_batch(predictions=texts)

    result = _perplexity_metric.compute(
        model_id=model_id,
        batch_size=4,
        add_start_token=True
    )
    
    return result["perplexities"]
