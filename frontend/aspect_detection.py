"""
ReviewSense - Aspect Detection & Label Normalization (Frontend)
Fast keyword matching for aspects and sentiment label normalization.
"""

import re
from typing import Any, Dict, List
import pandas as pd

ASPECT_KEYWORDS: Dict[str, List[str]] = {
    "Quality": ["quality", "material", "build", "durable", "broken", "sturdy", "cheap", "defective", "flimsy"],
    "Shipping": ["shipping", "delivery", "arrived", "courier", "late", "package", "packaging", "box", "fast"],
    "Price": ["price", "cost", "expensive", "cheap", "value", "money", "worth", "affordable", "deal"],
}

_ASPECT_PATTERNS = {
    name: re.compile(r"\b(?:" + "|".join(map(re.escape, kws)) + r")\b", re.IGNORECASE)
    for name, kws in ASPECT_KEYWORDS.items()
}

def detect_aspects(text: str) -> List[str]:
    """Returns detected aspects for a given review string."""
    if not isinstance(text, str) or not text.strip():
        return []
    clean_text = text.lower()
    return [name for name, pat in _ASPECT_PATTERNS.items() if pat.search(clean_text)]

def normalize_labels(series: pd.Series) -> pd.Series:
    """Normalizes various label encodings into negative / neutral / positive."""
    num = pd.to_numeric(series, errors="coerce")
    if num.notna().all():
        if set(num.unique()) <= {0, 1, 2}:
            return num.astype(int).map({0: "negative", 1: "neutral", 2: "positive"})
        return num.apply(lambda x: "negative" if x <= 2 else ("neutral" if x == 3 else "positive"))
    s = series.astype(str).str.strip().str.lower()
    return s.replace({"pos": "positive", "neg": "negative", "neu": "neutral"})
