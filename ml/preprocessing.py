import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

NEGATIONS = {"not", "no", "never", "nor", "none", "nothing",
             "neither", "nobody", "nowhere", "cannot"}
STOP_WORDS = sorted(ENGLISH_STOP_WORDS - NEGATIONS)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"n't\b", " not", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()