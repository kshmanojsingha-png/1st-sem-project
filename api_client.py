"""
ReviewSense - API Client Module
Handles communication between Streamlit frontend and FastAPI backend,
with automatic fallback to local ML predictor if the backend server is offline.
"""

import logging
import os
import requests
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("reviewsense.client")
DEFAULT_API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


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
            "error": "Backend server is not running",
        }
    except Exception as e:
        return {
            "online": False,
            "predictor_available": False,
            "url": url,
            "error": str(e),
        }


def _local_fallback_predict(review_text: str) -> Dict[str, Any]:
    """Runs prediction locally when FastAPI backend is offline."""
    from ml.predictor import predict
    from simran_all_in_one import detect_aspects

    clean_text = (review_text or "").strip()
    if not clean_text:
        return {
            "sentiment": "neutral",
            "aspects": [],
            "confidence": 0.0,
            "probabilities": {},
            "source": "Local ML Pipeline (Fallback)",
            "success": True,
            "error": None,
        }

    sentiment = predict([clean_text])[0]
    aspects = detect_aspects(clean_text)
    probs_dict = {}
    confidence = 0.0
    try:
        from ml.predictor import predict_proba
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


def predict_single(
    review_text: str,
    base_url: str = DEFAULT_API_URL,
    prefer_api: bool = True
) -> Dict[str, Any]:
    """
    Predicts sentiment and aspects for a single review.
    Tries the FastAPI backend first; gracefully falls back to local ML model.
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
                        "source": "FastAPI Backend (:8000)",
                        "success": True,
                        "error": None,
                    }
                logger.warning("API predict returned status %s", resp.status_code)
            except Exception as e:
                logger.info("FastAPI call error (%s); falling back to local ML", e)

    # Local fallback
    try:
        return _local_fallback_predict(clean_text)
    except Exception as e:
        logger.exception("Local predictor also failed")
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
                # Filter out pure empties for API payload, but keep position
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
                            "source": "FastAPI Backend",
                        })
                else:
                    raise RuntimeError(f"Backend API returned HTTP {resp.status_code}")

                if progress_callback:
                    processed = min(total, i + len(chunk))
                    progress_callback(processed / total, processed, total)

            if len(results) == total:
                return results, "FastAPI Backend (:8000)"
        except Exception as e:
            logger.warning("Backend batch execution failed (%s), switching to local model", e)
            results = []

    # Local batch fallback
    from ml.predictor import predict_batch as local_batch
    from simran_all_in_one import detect_aspects

    for i in range(0, total, chunk_size):
        chunk = review_texts[i:i + chunk_size]
        safe_chunk = [t if (isinstance(t, str) and t.strip()) else " " for t in chunk]
        try:
            chunk_preds = local_batch(safe_chunk)
        except Exception:
            chunk_preds = ["neutral"] * len(chunk)

        for text, pred in zip(chunk, chunk_preds):
            results.append({
                "sentiment": pred,
                "aspects": detect_aspects(text) if isinstance(text, str) else [],
                "source": "Local ML Pipeline (Fallback)",
            })

        if progress_callback:
            processed = min(total, i + len(chunk))
            progress_callback(processed / total, processed, total)

    return results, "Local ML Pipeline (Fallback)"
