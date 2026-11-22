import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import joblib
import matplotlib.pyplot as plt
import pandas as pd  # Moved to the top
from sklearn.metrics import (f1_score, accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)
from ml.data import load_split

LABELS = ["negative", "neutral", "positive"]

def main():
    _, X_test, _, y_test = load_split()
    model = joblib.load("models/sentiment_pipeline.joblib")
    pred = model.predict(X_test)

    # --- NEW CODE: Save predictions to CSV ---
    df = pd.DataFrame({
        "review_text": X_test,
        "actual": y_test,
        "predicted": pred
    })
    df.to_csv("data/predictions.csv", index=False)
    print("Saved data/predictions.csv successfully!")
    # -----------------------------------------

    metrics = {
        "macro_f1": round(f1_score(y_test, pred, average="macro"), 3),
        "weighted_f1": round(f1_score(y_test, pred, average="weighted"), 3),
        "accuracy": round(accuracy_score(y_test, pred), 3),
    }
    print(metrics)
    report = classification_report(y_test, pred, labels=LABELS, digits=3)
    print(report)

    with open("outputs/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    with open("outputs/classification_report.txt", "w") as f:
        f.write(report)

    cm = confusion_matrix(y_test, pred, labels=LABELS)
    
    pd.DataFrame(cm, index=LABELS, columns=LABELS).to_csv("outputs/confusion_matrix.csv")
    ConfusionMatrixDisplay(cm, display_labels=LABELS).plot(cmap="Blues")
    plt.title("Confusion matrix (held-out test set)")
    plt.savefig("outputs/confusion_matrix.png", dpi=150, bbox_inches="tight")
    print("Saved results to outputs/")

if __name__ == "__main__":
    main()