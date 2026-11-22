import importlib
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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

# --- Pydantic Schemas ---
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
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None
    error: Optional[str] = None

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResult]
    count: int

# --- Aspect Detection Loader ---
def _load_aspect_detector() -> Callable[[str], List[str]]:
    for mod_name in ("aspect_detection", "backend.aspect_detection", "simran_all_in_one"):
        try:
            mod = importlib.import_module(mod_name)
            for fn_name in ("detect_aspects", "get_aspects", "detect"):
                fn = getattr(mod, fn_name, None)
                if callable(fn):
                    logger.info("Aspect detector loaded from %s.%s", mod_name, fn_name)
                    return fn
        except Exception:
            continue

    from aspect_detection import detect_aspects
    return detect_aspects

DETECT_ASPECTS = _load_aspect_detector()

# --- Predictor Loader ---
_POSITIVE = re.compile(r"\b(?:good|great|love|excellent|fast|amazing|best|nice)\b", re.IGNORECASE)
_NEGATIVE = re.compile(r"\b(?:bad|worst|hate|slow|broken|expensive|poor|terrible)\b", re.IGNORECASE)

def _stub_predict(texts: List[str]) -> List[str]:
    results = []
    for review_text in texts:
        t = (review_text or "").lower()
        pos = len(set(_POSITIVE.findall(t)))
        neg = len(set(_NEGATIVE.findall(t)))
        if pos > neg:
            results.append("positive")
        elif neg > pos:
            results.append("negative")
        else:
            results.append("neutral")
    return results

def _load_predictor():
    errors: List[str] = []
    for mod_name in ("ml.predictor", "backend.ml.predictor", "predictor"):
        try:
            mod = importlib.import_module(mod_name)
            predict_fn = getattr(mod, "predict")
            batch_fn = getattr(mod, "predict_batch", None)
            proba_fn = getattr(mod, "predict_proba", None)
            logger.info("Real ML predictor loaded from %s (batch: %s, proba: %s)",
                        mod_name, callable(batch_fn), callable(proba_fn))
            return predict_fn, (batch_fn if callable(batch_fn) else None), (proba_fn if callable(proba_fn) else None), True
        except Exception as e:
            errors.append(f"{mod_name}: {type(e).__name__}: {e}")

    logger.warning("ML predictor not loaded - falling back to keyword stub. Errors: %s", errors)
    return _stub_predict, None, None, False

PREDICT_FN, PREDICT_BATCH_FN, PREDICT_PROBA_FN, PREDICTOR_IS_REAL = _load_predictor()

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
            logger.warning("Aspect detection failed: %s", e)
            aspects = []

    res = PredictionResult(sentiment=sentiment, aspects=aspects)

    if PREDICT_PROBA_FN is not None:
        try:
            p_dict = PREDICT_PROBA_FN([review_text])[0]
            res.probabilities = p_dict
            res.confidence = round(float(p_dict.get(sentiment, 0.0)), 4)
        except Exception:
            pass

    return res

def run_prediction(review_text: str) -> PredictionResult:
    try:
        raw = PREDICT_FN([review_text])[0]
        return _normalize(raw, review_text)
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

def _safe_single(review_text: str) -> PredictionResult:
    try:
        return _normalize(PREDICT_FN([review_text])[0], review_text)
    except Exception as e:
        logger.warning("Single prediction in batch failed: %s", e)
        return PredictionResult(sentiment="neutral", aspects=[], error=f"Prediction failed: {e}")

def run_batch(texts: List[str]) -> List[PredictionResult]:
    if PREDICT_BATCH_FN is not None:
        try:
            raws = list(PREDICT_BATCH_FN(texts))
            if len(raws) == len(texts):
                return [_normalize(r, t) for r, t in zip(raws, texts)]
            logger.warning("predict_batch returned %d results, expected %d - falling back to loop",
                           len(raws), len(texts))
        except Exception as e:
            logger.warning("predict_batch failed (%s) - falling back to loop", e)
    return [_safe_single(t) for t in texts]

# --- FastAPI Application ---
app = FastAPI(
    title="ReviewSense API",
    description="Production REST microservice for Aspect-Based Sentiment Analysis",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "ReviewSense Sentiment API",
        "version": "1.1.0",
        "status": "online",
        "docs_url": "/docs",
        "predictor_available": PREDICTOR_IS_REAL,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict_batch"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "predictor_available": PREDICTOR_IS_REAL
    }

@app.post("/predict", response_model=PredictionResult, response_model_exclude_none=True)
def predict_single(payload: ReviewInput):
    return run_prediction(payload.review_text)

@app.post("/predict_batch", response_model=BatchPredictionResponse, response_model_exclude_none=True)
def predict_batch(payload: BatchInput):
    texts = [r.review_text for r in payload.reviews]
    results = run_batch(texts)
    return BatchPredictionResponse(results=results, count=len(results))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
