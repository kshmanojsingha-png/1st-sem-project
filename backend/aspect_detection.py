"""
ReviewSense - Aspect Detection Module (Backend)
Fast regex-based keyword matching for product review aspect categorization.
"""

import re
from typing import Dict, List

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
    """Returns a list of aspects detected in the given review text."""
    if not isinstance(text, str) or not text.strip():
        return []
    clean_text = text.lower()
    return [name for name, pat in _ASPECT_PATTERNS.items() if pat.search(clean_text)]
