import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from ml.data import load_split
from ml.preprocessing import clean_text, STOP_WORDS

# Settings chosen by cross-validation on the training set (Day 2 tuning)
BEST = {"ngram_range": (1, 2), "min_df": 5, "C": 1.0}   # <- replace with your result

def main():
    X_train, X_test, y_train, y_test = load_split()
    model = Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=clean_text, stop_words=STOP_WORDS,
                                  ngram_range=BEST["ngram_range"],
                                  min_df=BEST["min_df"], max_features=50000)),
        ("clf", LogisticRegression(C=BEST["C"], max_iter=1000,
                                   class_weight="balanced"))
    ])
    model.fit(X_train, y_train)
    joblib.dump(model, "models/sentiment_pipeline.joblib")
    print("Model saved to models/sentiment_pipeline.joblib")

if __name__ == "__main__":
    main()