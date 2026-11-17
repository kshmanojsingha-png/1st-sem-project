import json
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (f1_score, accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)
from ml.data import load_split

LABELS = ["negative", "neutral", "positive"]

def main():
    _, X_test, _, y_test = load_split()
    model = joblib.load("models/sentiment_pipeline.joblib")
    pred = model.predict(X_test)

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
    import pandas as pd
    pd.DataFrame(cm, index=LABELS, columns=LABELS).to_csv("outputs/confusion_matrix.csv")
    ConfusionMatrixDisplay(cm, display_labels=LABELS).plot(cmap="Blues")
    plt.title("Confusion matrix (held-out test set)")
    plt.savefig("outputs/confusion_matrix.png", dpi=150, bbox_inches="tight")
    print("Saved results to outputs/")

if __name__ == "__main__":
    main()