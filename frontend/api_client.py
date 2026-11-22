"""
ReviewSense - API Client Module (Frontend)
Handles communication between Streamlit frontend and FastAPI backend,
with automatic fallback to local ML predictor or rule-based inference if the backend server is offline.
"""

import logging
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
import requests

logger = logging.getLogger("reviewsense.client")

def _get_default_backend_url() -> str:
    """Detects Backend URL from Streamlit secrets, environment variable, or default localhost."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
            return str(st.secrets["BACKEND_URL"]).rstrip("/")
    except Exception:
        pass
    return os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

DEFAULT_API_URL = _get_default_backend_url()

# Rule-based fallback keywords
_POSITIVE = re.compile(r"\b(?:good|great|love|excellent|fast|amazing|best|nice|happy|satisfied|delicious|fresh)\b", re.IGNORECASE)
_NEGATIVE = re.compile(r"\b(?:bad|worst|hate|slow|broken|expensive|poor|terrible|awful|horrible|stale|damaged)\b", re.IGNORECASE)

def _get_aspect_detector() -> Callable[[str], List[str]]:
    """Attempts to import detect_aspects from aspect_detection or simran_all_in_one."""
    for mod_name in ("aspect_detection", "simran_all_in_one"):
        try:
            mod = __import__(mod_name)
            fn = getattr(mod, "detect_aspects", None)
            if callable(fn):
                return fn
        except Exception:
            continue

    def _fallback_aspects(text: str) -> List[str]:
        t = (text or "").lower()
        res = []
        if any(w in t for w in ["quality", "material", "build", "durable", "broken"]):
            res.append("Quality")
        if any(w in t for w in ["shipping", "delivery", "arrived", "late", "package"]):
            res.append("Shipping")
        if any(w in t for w in ["price", "cost", "expensive", "cheap", "value", "money"]):
            res.append("Price")
        return res

    return _fallback_aspects

_DETECT_ASPECTS = _get_aspect_detector()

def check_api_health(base_url: str = DEFAULT_API_URL, timeout: float = 1.5) -> Dict[str, Any]:
    """Checks the health and availability of the FastAPI backend."""
    url = (base_url or DEFAULT_API_URL).rstrip("/")
    try:
        resp = requests.get(f"{url}/health", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "online": True,
                "predictor_available": data.get("predictor_available", False),
                "url": url,
                "error": None,
            }
        return {
            "online": False,
            "predictor_available": False,
            "url": url,
            "error": f"HTTP {resp.status_code}",
        }
    except requests.exceptions.ConnectionError:
        return {
            "online": False,
            "predictor_available": False,
            "url": url,
            "error": "Backend server is not running or unreachable",
        }
    except Exception as e:
        return {
            "online": False,
            "predictor_available": False,
            "url": url,
            "error": str(e),
        }

def _rule_based_predict(clean_text: str) -> Dict[str, Any]:
    """Lightweight rule-based fallback when neither backend nor local ML model is available."""
    t = clean_text.lower()
    pos = len(set(_POSITIVE.findall(t)))
    neg = len(set(_NEGATIVE.findall(t)))

    if pos > neg:
        sentiment = "positive"
        conf = 0.85
        probs = {"positive": 0.85, "neutral": 0.10, "negative": 0.05}
    elif neg > pos:
        sentiment = "negative"
        conf = 0.85
        probs = {"positive": 0.05, "neutral": 0.10, "negative": 0.85}
    else:
        sentiment = "neutral"
        conf = 0.60
        probs = {"positive": 0.20, "neutral": 0.60, "negative": 0.20}

    return {
        "sentiment": sentiment,
        "aspects": _DETECT_ASPECTS(clean_text),
        "confidence": conf,
        "probabilities": probs,
        "source": "Offline Fallback (Backend Sleeping / Unreachable)",
        "success": True,
        "error": None,
    }

def _local_fallback_predict(review_text: str) -> Dict[str, Any]:
    """Runs prediction locally when FastAPI backend is offline."""
    clean_text = (review_text or "").strip()
    if not clean_text:
        return {
            "sentiment": "neutral",
            "aspects": [],
            "confidence": 0.0,
            "probabilities": {},
            "source": "System",
            "success": True,
            "error": None,
        }

    # Attempt to use local ML model if installed
    try:
        from ml.predictor import predict, predict_proba
        sentiment = predict([clean_text])[0]
        aspects = _DETECT_ASPECTS(clean_text)
        probs_dict = {}
        confidence = 0.0
        try:
            probs_dict = predict_proba([clean_text])[0]
            confidence = round(float(probs_dict.get(sentiment, 0.0)), 4)
        except Exception:
            pass

        return {
            "sentiment": sentiment,
            "aspects": aspects,
            "confidence": confidence,
            "probabilities": probs_dict,
            "source": "Local ML Pipeline (Fallback)",
            "success": True,
            "error": None,
        }
    except Exception:
        # Fall back to rule-based offline predictor
        return _rule_based_predict(clean_text)

def predict_single(
    review_text: str,
    base_url: str = DEFAULT_API_URL,
    prefer_api: bool = True
) -> Dict[str, Any]:
    """
    Predicts sentiment and aspects for a single review.
    Tries the FastAPI backend first; gracefully falls back to local or rule-based model.
    """
    clean_text = (review_text or "").strip()
    if not clean_text:
        return {
            "sentiment": "neutral",
            "aspects": [],
            "confidence": 0.0,
            "probabilities": {},
            "source": "System",
            "success": False,
            "error": "Review text cannot be empty.",
        }

    url = (base_url or DEFAULT_API_URL).rstrip("/")

    if prefer_api:
        health = check_api_health(url, timeout=0.8)
        if health["online"]:
            try:
                resp = requests.post(
                    f"{url}/predict",
                    json={"review_text": clean_text},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "sentiment": data.get("sentiment", "neutral"),
                        "aspects": data.get("aspects", []),
                        "confidence": data.get("confidence"),
                        "probabilities": data.get("probabilities", {}),
                        "source": f"FastAPI Backend ({url})",
                        "success": True,
                        "error": None,
                    }
                logger.warning("API predict returned status %s", resp.status_code)
            except Exception as e:
                logger.info("FastAPI call error (%s); falling back", e)

    # Local fallback
    try:
        return _local_fallback_predict(clean_text)
    except Exception as e:
        logger.exception("Predictor fallback failed")
        return {
            "sentiment": "neutral",
            "aspects": [],
            "confidence": 0.0,
            "probabilities": {},
            "source": "Failed",
            "success": False,
            "error": str(e),
        }

def predict_batch(
    review_texts: List[str],
    base_url: str = DEFAULT_API_URL,
    chunk_size: int = 200,
    progress_callback: Optional[Callable[[float, int, int], None]] = None
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Predicts sentiment and aspects for a list of reviews.
    Chunks the input for optimal performance and streams progress.
    Returns: (list_of_results, execution_source_description)
    """
    if not review_texts:
        return [], "Empty Input"

    url = (base_url or DEFAULT_API_URL).rstrip("/")
    health = check_api_health(url)
    total = len(review_texts)
    results: List[Dict[str, Any]] = []

    # Attempt via FastAPI backend if healthy
    if health["online"]:
        try:
            for i in range(0, total, chunk_size):
                chunk = review_texts[i:i + chunk_size]
                payload = {
                    "reviews": [{"review_text": t if (isinstance(t, str) and t.strip()) else " "} for t in chunk]
                }
                resp = requests.post(f"{url}/predict_batch", json=payload, timeout=45.0)
                if resp.status_code == 200:
                    batch_res = resp.json().get("results", [])
                    for item in batch_res:
                        results.append({
                            "sentiment": item.get("sentiment", "neutral"),
                            "aspects": item.get("aspects", []),
                            "source": f"FastAPI Backend ({url})",
                        })
                else:
                    raise RuntimeError(f"Backend API returned HTTP {resp.status_code}")

                if progress_callback:
                    processed = min(total, i + len(chunk))
                    progress_callback(processed / total, processed, total)

            if len(results) == total:
                return results, f"FastAPI Backend ({url})"
        except Exception as e:
            logger.warning("Backend batch execution failed (%s), switching to local model", e)
            results = []

    # Local batch fallback (ML model if available, else rule-based)
    try:
        from ml.predictor import predict_batch as local_batch
        has_ml = True
    except Exception:
        has_ml = False

    for i in range(0, total, chunk_size):
        chunk = review_texts[i:i + chunk_size]
        safe_chunk = [t if (isinstance(t, str) and t.strip()) else " " for t in chunk]

        if has_ml:
            try:
                chunk_preds = local_batch(safe_chunk)
                source_label = "Local ML Pipeline (Fallback)"
            except Exception:
                chunk_preds = ["neutral"] * len(chunk)
                source_label = "Offline Fallback"
        else:
            chunk_preds = [_rule_based_predict(t)["sentiment"] for t in safe_chunk]
            source_label = "Offline Fallback (Backend Sleeping / Unreachable)"

        for text, pred in zip(chunk, chunk_preds):
            results.append({
                "sentiment": pred,
                "aspects": _DETECT_ASPECTS(text) if isinstance(text, str) else [],
                "source": source_label,
            })

        if progress_callback:
            processed = min(total, i + len(chunk))
            progress_callback(processed / total, processed, total)

    return results, source_label
