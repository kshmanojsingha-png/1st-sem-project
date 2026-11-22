from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "sentiment_pipeline.joblib"
_model = None

def _get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Model file not found. Run 'python -m ml.train' first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict(texts):
    if not isinstance(texts, list) or len(texts) == 0:
        raise ValueError("Please provide a list with at least one review.")
    for t in texts:
        if not isinstance(t, str) or not t.strip():
            raise ValueError("Review text is empty. Please enter a review.")
    return [str(label) for label in _get_model().predict(texts)]

def predict_batch(texts):
    if not isinstance(texts, list) or len(texts) == 0:
        return []
    safe_texts = [t if (isinstance(t, str) and t.strip()) else " " for t in texts]
    return [str(label) for label in _get_model().predict(safe_texts)]

def predict_proba(texts):
    if not isinstance(texts, list) or len(texts) == 0:
        return []
    safe_texts = [t if (isinstance(t, str) and t.strip()) else " " for t in texts]
    model = _get_model()
    probs = model.predict_proba(safe_texts)
    classes = list(model.classes_)
    return [{cls: float(p) for cls, p in zip(classes, row)} for row in probs]
