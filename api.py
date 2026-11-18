import importlib
import logging
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# --- FIXED PATH ---
# This goes up ONE level from api.py: backend -> Project
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("reviewsense.api")

MAX_BATCH_SIZE = 1000
MAX_REVIEW_LENGTH = 5000

NUMERIC_LABEL_MAP: Dict[str, str] = {
    "0": "negative",
    "1": "neutral",
    "2": "positive",
}
TEXT_LABEL_MAP: Dict[str, str] = {
    "pos": "positive",
    "positive": "positive",
    "neg": "negative",
    "negative": "negative",
    "neu": "neutral",
    "neutral": "neutral",
}

def normalize_sentiment(value: Any) -> str:
    s = str(value).strip().lower()
    if not s:
        return "neutral"
    if s in NUMERIC_LABEL_MAP:
        return NUMERIC_LABEL_MAP[s]
    if s.endswith(".0") and s[:-2] in NUMERIC_LABEL_MAP:
        return NUMERIC_LABEL_MAP[s[:-2]]
    return TEXT_LABEL_MAP.get(s, s)

class ReviewInput(BaseModel):
    review_text: str = Field(..., min_length=1, max_length=MAX_REVIEW_LENGTH)

    @field_validator("review_text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("review_text must not be empty or whitespace")
        return v.strip()

class BatchInput(BaseModel):
    reviews: List[ReviewInput] = Field(..., min_length=1, max_length=MAX_BATCH_SIZE)

class PredictionResult(BaseModel):
    sentiment: str
    aspects: List[str] = Field(default_factory=list)
    error: Optional[str] = None

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResult]
    count: int

ASPECT_KEYWORDS: Dict[str, List[str]] = {
    "Quality": ["quality", "material", "build", "durable", "broken"],
    "Shipping": ["shipping", "delivery", "arrived", "courier", "late"],
    "Price": ["price", "cost", "expensive", "cheap", "value", "money"],
}
_ASPECT_PATTERNS = {
    name: re.compile(r"\b(?:" + "|".join(map(re.escape, kws)) + r")\b")
    for name, kws in ASPECT_KEYWORDS.items()
}

def _local_detect_aspects(text: str) -> List[str]:
    t = (text or "").lower()
    return [name for name, pat in _ASPECT_PATTERNS.items() if pat.search(t)]

def _load_aspect_detector() -> Callable[[str], List[str]]:
    module_names = ("simran_all_in_one", "utils.aspect_detection", "aspect_detection", "backend.aspect_detection")
    func_names = ("detect_aspects", "get_aspects", "detect")
    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for fn_name in func_names:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                logger.info("Aspect detector loaded: %s.%s", mod_name, fn_name)
                return fn
    logger.warning("Simran ka aspect_detection module nahi mila - local keyword aspects use ho rahe hain")
    return _local_detect_aspects

DETECT_ASPECTS = _load_aspect_detector()

_POSITIVE = re.compile(r"\b(?:good|great|love|excellent|fast|amazing|best|nice)\b")
_NEGATIVE = re.compile(r"\b(?:bad|worst|hate|slow|broken|expensive|poor|terrible)\b")

def _stub_predict(review_text: str) -> Dict[str, Any]:
    text = (review_text or "").lower()
    pos = len(set(_POSITIVE.findall(text)))
    neg = len(set(_NEGATIVE.findall(text)))

    if pos > neg:
        sentiment = "positive"
    elif neg > pos:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {"sentiment": sentiment, "aspects": _local_detect_aspects(text)}

def _load_predictor():
    errors: List[str] = []
    for mod_name in ("ml.predictor", "backend.predictor", "predictor"):
        try:
            mod = importlib.import_module(mod_name)
            predict_fn = getattr(mod, "predict")
            batch_fn = getattr(mod, "predict_batch", None)
            logger.info("Real predictor loaded from %s (batch support: %s)", mod_name, callable(batch_fn))
            return predict_fn, (batch_fn if callable(batch_fn) else None), True
        except Exception as e:
            errors.append(f"{mod_name}: {type(e).__name__}: {e}")

    logger.warning("!!! REAL PREDICTOR LOAD NAHI HUA - STUB (keyword) MODEL CHAL RAHA HAI !!!")
    for err in errors:
        logger.warning("   import error -> %s", err)
    return _stub_predict, None, False

PREDICT_FN, PREDICT_BATCH_FN, PREDICTOR_IS_REAL = _load_predictor()

def _normalize(raw: Any, review_text: str) -> PredictionResult:
    if isinstance(raw, dict):
        sentiment = raw.get("sentiment", raw.get("label", "neutral"))
        aspects = raw.get("aspects", [])
    elif isinstance(raw, str):
        sentiment, aspects = raw, []
    elif isinstance(raw, (list, tuple)) and raw:
        sentiment, aspects = raw[0], (raw[1] if len(raw) > 1 else [])
    else:
        sentiment, aspects = "neutral", []

    sentiment = normalize_sentiment(sentiment)

    if aspects is None:
        aspects = []
    if not isinstance(aspects, list):
        aspects = [str(aspects)]
    aspects = [str(a) for a in aspects if str(a).strip()]

    if not aspects:
        try:
            aspects = [str(a) for a in (DETECT_ASPECTS(review_text) or []) if str(a).strip()]
        except Exception as e:
            logger.warning("Aspect detection fail hua: %s", e)
            aspects = []

    return PredictionResult(sentiment=sentiment, aspects=aspects)

def run_prediction(review_text: str) -> PredictionResult:
    try:
        # FIXED HERE: Passing as list and grabbing [0]
        raw = PREDICT_FN([review_text])[0]
        return _normalize(raw, review_text) 
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

def _safe_single(review_text: str) -> PredictionResult:
    try:
        return _normalize(PREDICT_FN([review_text])[0], review_text)
    except Exception as e:
        logger.warning("Batch me ek review fail hua: %s", e)
        return PredictionResult(sentiment="neutral", aspects=[], error=f"Prediction failed: {e}")

def run_batch(texts: List[str]) -> List[PredictionResult]:
    if PREDICT_BATCH_FN is not None:
        try:
            raws = list(PREDICT_BATCH_FN(texts))
            if len(raws) == len(texts):
                return [_normalize(r, t) for r, t in zip(raws, texts)]
            logger.warning("predict_batch ne %d results diye, %d chahiye the - loop par ja rahe hain",
                           len(raws), len(texts))
        except Exception as e:
            logger.warning("predict_batch fail hua (%s) - ek-ek review se try kar rahe hain", e)
    return [_safe_single(t) for t in texts]

app = FastAPI(title="ReviewSense API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "predictor_available": PREDICTOR_IS_REAL}

@app.post("/predict", response_model=PredictionResult, response_model_exclude_none=True)
def predict_single(payload: ReviewInput):
    return run_prediction(payload.review_text)

@app.post("/predict_batch", response_model=BatchPredictionResponse, response_model_exclude_none=True)
def predict_batch(payload: BatchInput):
    texts = [r.review_text for r in payload.reviews]
    results = run_batch(texts)
    return BatchPredictionResponse(results=results, count=len(results))

def predict_with_fallback(reviews: List[str], api_url: Optional[str] = None) -> List[Dict[str, Any]]:
    base = api_url or "http://127.0.0.1:8000"
    payload = {"reviews": [{"review_text": r} for r in reviews]}
    try:
        import requests
        resp = requests.post(f"{base}/predict_batch", json=payload, timeout=5.0)
        resp.raise_for_status()
        return resp.json()["results"]
    except Exception as e:
        logger.warning("API nahi mili (%s) - local predictor use ho raha hai", e)
        return [r.model_dump(exclude_none=True) for r in run_batch([t.strip() for t in reviews])]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)