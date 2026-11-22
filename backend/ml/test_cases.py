import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.predictor import predict

CASES = [
    ("Absolutely loved it, delicious and fresh.", "positive"),
    ("Best purchase I have made, highly recommend.", "positive"),
    ("Terrible, it arrived broken and tasted awful.", "negative"),
    ("Worst product ever, complete waste of money.", "negative"),
    ("It was okay, nothing special.", "neutral"),
    ("Average product, neither good nor bad.", "neutral"),
    ("Not good at all.", "negative"),
    ("Never again.", "negative"),
    ("Not bad.", "positive"),
    ("Not happy with the quality.", "negative"),
]

results = predict([c[0] for c in CASES])
correct = 0
for (text, expected), got in zip(CASES, results):
    ok = got == expected
    correct += ok
    print(f"{'OK  ' if ok else 'MISS'} expected={expected:9} got={got:9} | {text}")
print(f"\n{correct}/{len(CASES)} as expected")