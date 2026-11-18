"""
ReviewSense (Group D) - SIMRAN: Analytics, Testing & Documentation
ONE FILE. Copy it into your project folder (next to app.py) and run from that folder.

Install:
  pip install pandas plotly matplotlib scikit-learn kaleido streamlit python-pptx

Commands:
  python simran_all_in_one.py all        # runs everything below in order (recommended)
  python simran_all_in_one.py eda        # class distribution + chart
  python simran_all_in_one.py aspects    # aspect detection demo
  python simran_all_in_one.py coverage   # how many real reviews get an aspect tag
  python simran_all_in_one.py eval       # confusion matrix + Macro/Weighted F1
  python simran_all_in_one.py charts     # sentiment donut + aspect charts (needs review text in predictions CSV)
  python simran_all_in_one.py test       # test cases + saves test_results.txt
  python simran_all_in_one.py docs       # README.md + PPT_outline.md, filled with your real numbers
  python simran_all_in_one.py ppt        # ReviewSense_GroupD.pptx (12+ slides, real numbers and charts)
  streamlit run simran_all_in_one.py     # standalone dashboard (for demo / screenshots)

In Atik's app.py:  from simran_all_in_one import show_dashboard

Everything it creates goes into the report_assets/ folder (plus README.md and the .pptx).
"""
import glob
import os
import re
import sys
from typing import List

# =====================================================================================
# CONFIG - edit this section only
# =====================================================================================
DATA_PATH = "data/reviews.csv"           # dataset used for EDA (review text + rating or label)
PRED_CSV = "data/predictions.csv"        # evaluate.py output (true + predicted labels)
OUT_DIR = "report_assets"                # charts, confusion matrix, test results go here
SCREENSHOT_DIR = "screenshots"           # put app screenshots (.png/.jpg) here; the PPT adds them
SAMPLE_N = 5000                          # reviews sampled by the `coverage` command

DATASET_NAME = "Amazon Fine Food Reviews (Kaggle), accessed 15 November 2026"   # change if you used Yelp
MODEL_NAME = "TF-IDF + Logistic Regression (scikit-learn), saved with Joblib"
LABEL_RULE = "rating 1-2 = negative, 3 = neutral, 4-5 = positive"

# Set these to match what your team REALLY built. The README only lists features that are True.
HAS_CSV_BATCH = True        # CSV upload + results table + download
HAS_DASHBOARD = True        # donut chart, aspect charts, aspect filter
HAS_FASTAPI = True          # FastAPI endpoint (optional in the revised PRD)

# Files listed in the README project structure (only those that exist are listed).
PROJECT_FILES = [
    (["train.py"], "trains the model and saves it with Joblib"),
    (["evaluate.py"], "held-out test evaluation (Macro-F1, Weighted-F1, confusion matrix)"),
    (["predictor.py", "backend/predictor.py"], "loads the saved model; predict(text) returns the sentiment"),
    (["test_cases.py"], "model test cases"),
    (["app.py", "streamlit_app.py"], "Streamlit web page"),
    (["simran_all_in_one.py"], "aspect tags, charts, evaluation visuals, tests, documentation generator"),
]

# Where the sentiment tests look for the predict() function: (module, function name)
PREDICTOR_CANDIDATES = [
    ("ml.predictor", "predict"),         # <--- ADDED MANOJ'S ML FOLDER HERE
    ("backend.predictor", "predict"), 
    ("predictor", "predict"), 
    ("src.predictor", "predict"),
    ("utils.predictor", "predict"), 
    ("predictor", "predict_sentiment"),
    ("backend.predictor", "predict_sentiment"),
]

CLASS_ORDER = ["negative", "neutral", "positive"]
COLORS = {"positive": "#2ca02c", "neutral": "#f2c744", "negative": "#d62728"}

# Column names are auto-detected from these lists (first match wins, case-insensitive).
TEXT_CANDIDATES = ["review_text", "Text", "text", "review", "reviewText", "content", "comment"]
LABEL_CANDIDATES = ["label", "sentiment", "Score", "score", "rating", "stars"]
TRUE_CANDIDATES = ["true_label", "y_true", "actual", "true", "label"]
PRED_CANDIDATES = ["pred_label", "y_pred", "predicted", "prediction", "pred"]
SENTIMENT_CANDIDATES = ["sentiment", "pred_label", "prediction", "predicted", "label"]


# =====================================================================================
# HELPERS
# =====================================================================================
def _first_col(df, candidates, what):
    cols = list(df.columns)
    for c in candidates:
        if c in cols:
            return c
    lower = {str(c).lower(): c for c in cols}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    raise KeyError(f"No {what} column found. Looked for {candidates}. "
                   f"Columns in your file: {cols}. Add the right name to the CANDIDATES list at the top.")


def normalize_labels(series):
    """Turn labels into negative / neutral / positive.
    Accepts text labels, 0/1/2 (alphabetical encoding), or 1-5 star ratings."""
    import pandas as pd
    num = pd.to_numeric(series, errors="coerce")
    if num.notna().all():
        if set(num.unique()) <= {0, 1, 2}:
            return num.astype(int).map({0: "negative", 1: "neutral", 2: "positive"})
        return num.apply(lambda x: "negative" if x <= 2 else ("neutral" if x == 3 else "positive"))
    s = series.astype(str).str.strip().str.lower()
    return s.replace({"pos": "positive", "neg": "negative", "neu": "neutral"})


def _norm_one(v):
    """Normalise one prediction (str / dict / tuple / number) to a label string."""
    if isinstance(v, dict):
        v = v.get("sentiment", v.get("label", v.get("prediction")))
    elif isinstance(v, (list, tuple)):
        v = v[0] if v else None
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return {0: "negative", 1: "neutral", 2: "positive"}.get(int(v), str(v))
    return str(v).strip().lower()


def _save_fig(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.write_html(os.path.join(OUT_DIR, name + ".html"))
    try:
        fig.write_image(os.path.join(OUT_DIR, name + ".png"))
    except Exception as e:  # kaleido missing
        print(f"  (PNG for {name} not saved - pip install kaleido) {type(e).__name__}")


def _find_file(names):
    if isinstance(names, str):
        names = [names]
    for n in names:
        for pat in (n, f"*/{n}", f"*/*/{n}"):
            hits = [h for h in sorted(glob.glob(pat)) if not any(x in h for x in ("venv", "site-packages", "node_modules"))]
            if hits:
                return hits[0].replace("\\", "/")
    return None


def _safe_write(name, text):
    """Never overwrite a file you already have: writes name_new.ext instead."""
    path = name
    if os.path.exists(path):
        base, ext = os.path.splitext(name)
        path = f"{base}_new{ext}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


# =====================================================================================
# ASPECT DETECTION (rule-based)
# =====================================================================================
ASPECT_KEYWORDS = {
    "Quality": ["quality", "durable", "durability", "build", "material", "broken", "broke",
                "damaged", "defective", "defect", "faulty", "sturdy", "flimsy",
                "stopped working", "works well", "fake", "genuine", "original", "poor",
                "excellent", "worn", "stitching",
                # food products
                "fresh", "stale", "expired", "rotten", "spoiled", "rancid", "moldy",
                "ingredient", "organic", "artificial"],
    "Shipping": ["shipping", "shipped", "delivery", "delivered", "arrived", "arrive", "late",
                 "delay", "delayed", "courier", "package", "packaging", "packed", "parcel",
                 "dispatch", "on time", "fast delivery", "tracking", "transit", "wrong item"],
    "Price": ["price", "pricing", "cost", "costly", "expensive", "cheap", "cheaper", "affordable",
              "worth", "value for money", "overpriced", "discount", "offer", "budget", "money",
              "pricey", "refund", "bargain", "bucks"],
}
# whole words only; an optional plural (s / es) is allowed
_PATTERNS = {a: [re.compile(r"\b" + re.escape(k) + r"(?:s|es)?\b", re.I) for k in kws]
             for a, kws in ASPECT_KEYWORDS.items()}


def detect_aspects(text) -> List[str]:
    """Aspects found in the review; [] if none (or if the input is empty / not text)."""
    if not isinstance(text, str) or not text.strip():
        return []
    return [a for a, pats in _PATTERNS.items() if any(p.search(text) for p in pats)]


def add_aspect_column(df, text_col=None):
    df = df.copy()
    text_col = text_col or _first_col(df, TEXT_CANDIDATES, "review text")
    df["aspects"] = df[text_col].apply(detect_aspects)
    return df


def filter_by_aspect(df, aspect):
    if aspect == "All":
        return df
    if aspect == "No aspect":
        return df[df["aspects"].apply(len) == 0]
    return df[df["aspects"].apply(lambda a: aspect in a)]


# =====================================================================================
# CHARTS (Plotly)
# =====================================================================================
def sentiment_donut(df, sentiment_col="sentiment"):
    import plotly.express as px
    c = df[sentiment_col].value_counts().reset_index()
    c.columns = ["sentiment", "count"]
    fig = px.pie(c, names="sentiment", values="count", hole=0.5, color="sentiment",
                 color_discrete_map=COLORS, title="Sentiment Distribution")
    fig.update_traces(textinfo="percent+label")
    return fig


def aspect_bar(df, aspects_col="aspects"):
    import plotly.express as px
    c = df[aspects_col].explode().dropna().value_counts().reset_index()
    c.columns = ["aspect", "count"]
    return px.bar(c, x="aspect", y="count", text="count", title="Aspect Mentions")


def aspect_sentiment_chart(df, sentiment_col="sentiment", aspects_col="aspects"):
    import plotly.express as px
    ex = df.explode(aspects_col).dropna(subset=[aspects_col])
    g = ex.groupby([aspects_col, sentiment_col]).size().reset_index(name="count")
    return px.bar(g, x=aspects_col, y="count", color=sentiment_col, barmode="group",
                  color_discrete_map=COLORS, title="Sentiment by Aspect")


def _plot(container, fig):
    """Works on old and new Streamlit (use_container_width is deprecated in new versions)."""
    import inspect
    if "width" in inspect.signature(container.plotly_chart).parameters:
        container.plotly_chart(fig, width="stretch")
    else:
        container.plotly_chart(fig, use_container_width=True)


def show_dashboard(results_df, text_col=None, sentiment_col=None):
    """Streamlit block. results_df needs a review-text column and a sentiment column.
    Column names are auto-detected; the aspects column is added automatically."""
    import streamlit as st
    results_df = results_df.copy()
    if "aspects" not in results_df.columns:
        results_df = add_aspect_column(results_df, text_col)
    sc = sentiment_col or _first_col(results_df, SENTIMENT_CANDIDATES, "sentiment")
    results_df["sentiment"] = normalize_labels(results_df[sc])

    choice = st.selectbox("Filter by aspect", ["All", "Quality", "Shipping", "Price", "No aspect"])
    view = filter_by_aspect(results_df, choice)
    if view.empty:
        st.info("No reviews found for this filter.")
        return
    c1, c2 = st.columns(2)
    _plot(c1, sentiment_donut(view))
    if view["aspects"].explode().notna().any():
        _plot(c2, aspect_bar(view))
        _plot(st, aspect_sentiment_chart(view))
    shown = view.copy()
    shown["aspects"] = shown["aspects"].apply(lambda a: ", ".join(a))
    st.dataframe(shown)


# =====================================================================================
# EDA
# =====================================================================================
def run_eda():
    import pandas as pd
    import plotly.express as px
    if not os.path.exists(DATA_PATH):
        print(f"{DATA_PATH} not found. Change DATA_PATH at the top of this file.")
        return
    df = pd.read_csv(DATA_PATH)
    tc = _first_col(df, TEXT_CANDIDATES, "review text")
    lc = _first_col(df, LABEL_CANDIDATES, "label / rating")
    df = df.dropna(subset=[lc]).copy()
    df["label_norm"] = normalize_labels(df[lc])
    print(f"Using text column '{tc}' and label column '{lc}' (numeric ratings are mapped: {LABEL_RULE})")
    print("Shape:", df.shape)
    print(df.isna().sum())
    counts = df["label_norm"].value_counts().reindex(CLASS_ORDER).fillna(0).astype(int)
    print(counts)
    print((counts / counts.sum() * 100).round(1))
    c = counts.reset_index()
    c.columns = ["class", "count"]
    fig = px.bar(c, x="class", y="count", text="count", color="class", color_discrete_map=COLORS,
                 title="Class Distribution of Reviews")
    fig.update_layout(showlegend=False)
    _save_fig(fig, "class_distribution")
    df["n_words"] = df[tc].astype(str).str.split().str.len()
    print(df.groupby("label_norm")["n_words"].describe().round(1))
    print(f"Saved charts in {OUT_DIR}/")


def run_coverage():
    """Shows how many real reviews get at least one aspect tag, so keywords can be tuned."""
    import pandas as pd
    if not os.path.exists(DATA_PATH):
        print(f"{DATA_PATH} not found.")
        return
    df = pd.read_csv(DATA_PATH)
    tc = _first_col(df, TEXT_CANDIDATES, "review text")
    df = df.dropna(subset=[tc])
    if len(df) > SAMPLE_N:
        df = df.sample(SAMPLE_N, random_state=42)
    df = add_aspect_column(df, tc)
    n = len(df)
    print(f"Sample: {n} reviews")
    for a in ASPECT_KEYWORDS:
        k = int(df["aspects"].apply(lambda x: a in x).sum())
        print(f"  {a:9} {k:5}  ({k / n * 100:.1f}%)")
    none = int((df["aspects"].apply(len) == 0).sum())
    multi = int((df["aspects"].apply(len) >= 2).sum())
    print(f"  No aspect {none:5}  ({none / n * 100:.1f}%)")
    print(f"  2+ aspects {multi:4}  ({multi / n * 100:.1f}%)")
    print("\nExamples with NO aspect (add keywords if you see a pattern):")
    for t in df[df["aspects"].apply(len) == 0][tc].head(5):
        print("  -", str(t)[:120])


# =====================================================================================
# EVALUATION
# =====================================================================================
def load_predictions(path=None):
    import pandas as pd
    path = path or PRED_CSV
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    tc = _first_col(df, TRUE_CANDIDATES, "true-label")
    pc = _first_col(df, PRED_CANDIDATES, "predicted-label")
    df = df.dropna(subset=[tc, pc]).copy()
    df["true_label"] = normalize_labels(df[tc])
    df["pred_label"] = normalize_labels(df[pc])
    return df


def _present_labels(y_true, y_pred):
    seen = set(y_true) | set(y_pred)
    return [c for c in CLASS_ORDER if c in seen]


def evaluation_metrics(y_true, y_pred):
    from sklearn.metrics import accuracy_score, classification_report, f1_score
    labels = _present_labels(y_true, y_pred)
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0),
        "accuracy": accuracy_score(y_true, y_pred),
        "labels": labels,
        "per_class": classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0),
        "report": classification_report(y_true, y_pred, labels=labels, zero_division=0),
    }


def confusion_matrix_figure(y_true, y_pred, labels=None, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
    labels = labels or _present_labels(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    if path:
        fig.savefig(path, dpi=150)
    return fig


def run_eval():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_predictions()
    if df is None:
        print(f"{PRED_CSV} not found -> running on DEMO data (not your real results). "
              f"Ask Manoj for the predictions CSV (true + predicted label).")
        y_true = ["positive", "negative", "neutral", "positive", "negative", "neutral"]
        y_pred = ["positive", "negative", "positive", "positive", "neutral", "neutral"]
        real = False
    else:
        y_true, y_pred, real = df["true_label"], df["pred_label"], True
    m = evaluation_metrics(y_true, y_pred)
    print(m["report"])
    print(f"Accuracy: {m['accuracy']:.3f} | Macro-F1: {m['macro_f1']:.3f} | Weighted-F1: {m['weighted_f1']:.3f}")
    confusion_matrix_figure(y_true, y_pred, m["labels"], os.path.join(OUT_DIR, "confusion_matrix.png"))
    with open(os.path.join(OUT_DIR, "classification_report.txt"), "w", encoding="utf-8") as f:
        f.write(("" if real else "DEMO DATA - NOT REAL RESULTS\n") + m["report"])
    print(f"Saved confusion_matrix.png and classification_report.txt in {OUT_DIR}/")


def run_charts():
    """Dashboard charts from the predictions CSV (needs a review-text column in that file)."""
    df = load_predictions()
    if df is None:
        print(f"{PRED_CSV} not found - skipping charts.")
        return
    try:
        tc = _first_col(df, TEXT_CANDIDATES, "review text")
    except KeyError:
        print("predictions CSV has no review-text column - asking Manoj to include the review text "
              "in predictions.csv lets this make the aspect charts. Donut only.")
        tc = None
    df["sentiment"] = df["pred_label"]
    _save_fig(sentiment_donut(df), "sentiment_donut")
    if tc:
        df = add_aspect_column(df, tc)
        if df["aspects"].explode().notna().any():
            _save_fig(aspect_bar(df), "aspect_mentions")
            _save_fig(aspect_sentiment_chart(df), "aspect_sentiment")
    print(f"Saved charts in {OUT_DIR}/")


# =====================================================================================
# TEST CASES
# =====================================================================================
ASPECT_CASES = [  # (review, expected aspects, type)
    ("The quality is excellent and very durable", ["Quality"], "positive"),
    ("Product broke in two days, very poor build", ["Quality"], "negative"),
    ("It is okay, nothing special", [], "neutral / no-aspect"),
    ("Good quality but delivery was late", ["Quality", "Shipping"], "multi-aspect"),
    ("Expensive, late delivery and cheap material", ["Quality", "Shipping", "Price"], "multi-aspect"),
    ("Stale and expired when it arrived", ["Quality", "Shipping"], "multi-aspect (food)"),
    ("Fresh taste, great value for money", ["Quality", "Price"], "multi-aspect (food)"),
    ("Delivery was fast and the package was neat", ["Shipping"], "single aspect"),
    ("Total waste of money", ["Price"], "negative"),
    ("Nice", [], "no-aspect"),
    ("", [], "empty input"),
    ("PRICE is too high", ["Price"], "case-insensitive"),
    (None, [], "None input"),
    (123, [], "non-text input"),
]
SENTIMENT_CASES = [  # (review, expected sentiment)
    ("Absolutely love it, works perfectly", "positive"),
    ("Delicious and fresh, will buy again", "positive"),
    ("Terrible, waste of money", "negative"),
    ("Awful taste, never buying this again", "negative"),
    ("It is fine, average product", "neutral"),
]


def load_predict_fn():
    import importlib
    for mod, fn in PREDICTOR_CANDIDATES:
        try:
            f = getattr(importlib.import_module(mod), fn, None)
        except ImportError:
            continue
        except Exception as e:  # the module exists but failed to load
            print(f"  (found {mod} but it failed to import: {type(e).__name__}: {e})")
            continue
        if callable(f):
            return f, f"{mod}.{fn}"
    return None, None


def build_test_report():
    """Runs all tests. Returns a dict with a printable 'text' and structured 'rows'."""
    rows, lines = [], []
    lines.append(f"{'Input':48} {'Expected':28} {'Actual':28} Result")
    a_pass = 0
    for text, exp, kind in ASPECT_CASES:
        got = detect_aspects(text)
        ok = sorted(got) == sorted(exp)
        a_pass += ok
        res = "PASS" if ok else "FAIL"
        lines.append(f"{repr(text)[:46]:48} {str(exp):28} {str(got):28} {res}  [{kind}]")
        rows.append((kind, repr(text)[:40], ", ".join(exp) or "none", ", ".join(got) or "none", res))
    lines.append(f"\n{a_pass}/{len(ASPECT_CASES)} aspect tests passed")

    s_pass, s_total, s_note = 0, 0, ""
    predict, where = load_predict_fn()
    lines.append("")
    if predict is None:
        s_note = ("Sentiment tests SKIPPED: predict() function not found. "
                  "Edit PREDICTOR_CANDIDATES at the top of this file.")
        lines.append(s_note)
    else:
        lines.append(f"Sentiment tests using {where}")
        lines.append(f"{'Input':48} {'Expected':12} {'Actual':12} Result")
        for text, want in SENTIMENT_CASES:
            s_total += 1
            try:
                # FIXED HERE: Passed as a list [text]
                got = _norm_one(predict([text]))
            except Exception as e:
                got = f"ERROR {type(e).__name__}"
            ok = got == want
            s_pass += ok
            res = "PASS" if ok else "FAIL"
            lines.append(f"{repr(text)[:46]:48} {want:12} {got:12} {res}")
            rows.append(("sentiment", repr(text)[:40], want, got, res))
        lines.append(f"\n{s_pass}/{s_total} sentiment tests passed "
                     f"(a FAIL on 'neutral' is common for TF-IDF models - mention it under limitations)")
    return {"text": "\n".join(lines), "rows": rows, "a_pass": a_pass, "a_total": len(ASPECT_CASES),
            "s_pass": s_pass, "s_total": s_total, "s_note": s_note}


def run_tests():
    os.makedirs(OUT_DIR, exist_ok=True)
    rep = build_test_report()
    print(rep["text"])
    out_path = os.path.join(OUT_DIR, "test_results.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rep["text"])
        print(f"\nSaved {OUT_DIR}/test_results.txt")
    except Exception as e:
        print(f"\nNote: Could not write to {out_path} ({e})")
    return rep


# =====================================================================================
# FACTS used by README and PPT (all real numbers come from your files)
# =====================================================================================
def gather_facts():
    import pandas as pd
    facts = {"n_rows": None, "dist": None, "metrics": None, "n_test": None, "missing": []}
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            lc = _first_col(df, LABEL_CANDIDATES, "label / rating")
            df = df.dropna(subset=[lc])
            facts["n_rows"] = len(df)
            facts["dist"] = normalize_labels(df[lc]).value_counts().reindex(CLASS_ORDER).fillna(0).astype(int)
        except Exception as e:
            facts["missing"].append(f"dataset ({type(e).__name__}: {e})")
    else:
        facts["missing"].append(f"dataset ({DATA_PATH} not found)")
    try:
        pdf = load_predictions()
        if pdf is not None:
            facts["metrics"] = evaluation_metrics(pdf["true_label"], pdf["pred_label"])
            facts["n_test"] = len(pdf)
        else:
            facts["missing"].append(f"evaluation ({PRED_CSV} not found)")
    except Exception as e:
        facts["missing"].append(f"evaluation ({type(e).__name__}: {e})")
    return facts


def _dist_text(facts):
    d = facts["dist"]
    if d is None:
        return None
    tot = int(d.sum())
    return ", ".join(f"{k} {int(v):,} ({v / tot * 100:.1f}%)" for k, v in d.items())


def _features():
    f = ["Type one review and get its predicted sentiment (positive / neutral / negative)",
         "Rule-based aspect tags: Quality, Shipping, Price (a review can have several or none)"]
    if HAS_CSV_BATCH:
        f.append("CSV batch analysis with a results table and download")
    if HAS_DASHBOARD:
        f.append("Dashboard: sentiment donut chart, aspect charts, aspect filter")
    if HAS_FASTAPI:
        f.append("FastAPI endpoint for batch predictions")
    return f


# =====================================================================================
# README + PPT OUTLINE GENERATOR
# =====================================================================================
def build_readme(facts, rep):
    L = []
    a = L.append
    a("# ReviewSense - Multi-Aspect Product Review & Customer Sentiment Hub")
    a("**Group D** | Atik Hussain, Biki Sharmah, Simran Saikia, Manoj\n")
    a("## 1. Overview")
    a("ReviewSense reads a product review and predicts whether it is positive, neutral or negative, "
      "and tags which aspects it talks about (Quality, Shipping, Price).\n")
    a("## 2. Features")
    for f in _features():
        a(f"- {f}")
    a("\n## 3. Project Structure")
    a("```")
    for names, desc in PROJECT_FILES:
        found = _find_file(names)
        if found:
            a(f"{found:32} {desc}")
    a("```\n")
    a("## 4. Installation")
    a("```")
    a("pip install -r requirements.txt" if _find_file("requirements.txt")
      else "pip install streamlit pandas scikit-learn joblib plotly matplotlib")
    a("```\n")
    a("## 5. How to Run")
    a("```")
    train, ev, app = _find_file("train.py"), _find_file("evaluate.py"), _find_file(["app.py", "streamlit_app.py"])
    if train:
        a(f"python {train}      # train and save the model")
    if ev:
        a(f"python {ev}   # evaluate on the held-out test set")
    a(f"streamlit run {app or 'app.py'}")
    if HAS_FASTAPI:
        a("uvicorn backend.api:app --reload   # optional API")
    a("```\n")
    a("## 6. Methodology")
    a(f"- **Dataset:** {DATASET_NAME}.")
    if facts["n_rows"]:
        a(f"- **Size used:** {facts['n_rows']:,} reviews. Class distribution: {_dist_text(facts)}.")
    a(f"- **Labels:** only the review text and the star rating are used; {LABEL_RULE}.")
    a(f"- **Model:** {MODEL_NAME}.")
    a("- **Metrics:** Macro-F1 (main metric, because the classes are imbalanced), Weighted-F1 and the "
      "confusion matrix, all on a held-out test set.")
    a("- **Aspect detection:** rule-based whole-word keyword matching. A review can have several "
      "aspects or none. It shows the topic, not the sentiment about that topic.\n")
    a("## 7. Results")
    m = facts["metrics"]
    if m:
        a(f"Test set: {facts['n_test']:,} reviews. **Macro-F1 = {m['macro_f1']:.3f}**, "
          f"**Weighted-F1 = {m['weighted_f1']:.3f}**, accuracy = {m['accuracy']:.3f}.\n")
        a("| Class | Precision | Recall | F1 | Support |")
        a("| --- | --- | --- | --- | --- |")
        for c in m["labels"]:
            r = m["per_class"][c]
            a(f"| {c} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1-score']:.3f} | {int(r['support'])} |")
        a("\n![Confusion matrix](report_assets/confusion_matrix.png)\n")
    else:
        a("Evaluation results were not available when this file was generated. "
          "Run `python simran_all_in_one.py eval` and generate the README again.\n")
    if os.path.exists(os.path.join(OUT_DIR, "class_distribution.png")):
        a("![Class distribution](report_assets/class_distribution.png)\n")
    shots = _screenshots()
    for s in shots:
        a(f"![{os.path.splitext(os.path.basename(s))[0]}]({s.replace(os.sep, '/')})")
    a("\n## 8. Testing")
    a("```")
    a(rep["text"])
    a("```\n")
    a("## 9. Limitations & Future Work")
    a("- Keyword rules miss synonyms and sarcasm, and ignore negation (\"not durable\" is still tagged Quality).")
    a("- Aspect tags show the topic, not the sentiment about that topic.")
    a("- A TF-IDF model has no sense of word order, so the neutral class is the hardest.")
    a("- Future work: BERT-style model, aspect-level sentiment, more languages.\n")
    a("## 10. Team")
    a("Manoj - data and ML model | Atik - Streamlit UI | Biki - integration and support | "
      "Simran - testing, README, PPT, documentation")
    return "\n".join(L) + "\n"


def build_outline():
    qa = [
        ("Why Macro-F1?", "It treats every class equally, so a model cannot look good just by predicting the big class. Accuracy misleads on imbalanced data."),
        ("Macro vs Weighted F1?", "Macro = plain average of the class F1 scores. Weighted = average weighted by how many reviews each class has."),
        ("What is a confusion matrix?", "A table of actual vs predicted classes. The diagonal is correct predictions."),
        ("What is TF-IDF?", "It turns text into numbers: words frequent in a review but rare across all reviews get a high weight."),
        ("Why Logistic Regression?", "Fast, easy to explain, a strong baseline for text, and simple to save and load with Joblib."),
        ("How were labels made?", f"From the star rating: {LABEL_RULE}."),
        ("How do you avoid leakage?", "The test set is held out and never used for training. Check in train.py that TF-IDF is fitted on the training split only."),
        ("Why rule-based aspects?", "Simple, explainable, needs no labelled aspect data, and fits the time limit."),
        ("Limitations?", "Synonyms, sarcasm, negation; the neutral class is hardest; aspect tags show the topic, not the sentiment."),
        ("Several or no aspects?", "A list is returned; the list is empty if nothing matches."),
        ("Future work?", "BERT-style model, aspect-based sentiment, more languages."),
    ]
    if HAS_FASTAPI:
        qa.insert(9, ("Why FastAPI?", "It keeps the UI separate from the model and gives a clean batch endpoint."))
    L = ["# PPT Outline (12 slides + screenshots)",
         "1 Title | 2 Problem | 3 Objectives | 4 Dataset + class chart | 5 Architecture | 6 Sentiment model",
         "7 Aspect detection | 8 Evaluation (confusion matrix, F1) | 9 Live demo | (screenshots) | "
         "10 Testing table | 11 Limitations & future work | 12 Conclusion / Q&A\n",
         "# Demo script",
         "1. Type a positive review -> sentiment shown",
         "2. Type \"Good quality but late delivery\" -> two aspect tags (Quality, Shipping)",
         "3. Type a one-word review (\"Nice\") -> no aspect"]
    if HAS_CSV_BATCH:
        L.append("4. Upload a CSV -> results table" + (" + donut chart" if HAS_DASHBOARD else ""))
        if HAS_DASHBOARD:
            L.append("5. Use the aspect filter \"Shipping\"")
        L.append("6. Download the results CSV")
        L.append("7. Upload a CSV with the wrong column -> friendly error message")
    L.append("\n# Theory Q&A")
    for q, ans in qa:
        L.append(f"- **{q}** {ans}")
    return "\n".join(L) + "\n"


def make_docs():
    os.makedirs(OUT_DIR, exist_ok=True)
    facts = gather_facts()
    rep = build_test_report()
    r1 = _safe_write("README.md", build_readme(facts, rep))
    r2 = _safe_write("PPT_outline.md", build_outline())
    print(f"Created {r1} and {r2}")
    if facts["missing"]:
        print("Not filled in (run the matching command, then run docs again):")
        for m in facts["missing"]:
            print("  -", m)


# =====================================================================================
# POWERPOINT GENERATOR
# =====================================================================================
def _screenshots():
    files = []
    for ext in ("png", "jpg", "jpeg"):
        files += glob.glob(os.path.join(SCREENSHOT_DIR, f"*.{ext}"))
    return sorted(files)[:6]


def make_ppt(path="ReviewSense_GroupD.pptx"):
    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches, Pt
    except ImportError:
        print("python-pptx is missing -> pip install python-pptx")
        return
    from PIL import Image

    facts, rep = gather_facts(), build_test_report()
    NAVY, WHITE, GREY = RGBColor(0x1F, 0x2A, 0x44), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0x33, 0x33, 0x33)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def band(slide, text, height=1.2, size=32):
        shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(height))
        shp.fill.solid()
        shp.fill.fore_color.rgb = NAVY
        shp.line.fill.background()
        tf = shp.text_frame
        tf.margin_left = Inches(0.6)
        tf.text = text
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        p.runs[0].font.size, p.runs[0].font.bold, p.runs[0].font.color.rgb = Pt(size), True, WHITE

    def bullets_box(slide, items, left, top, width, height, size=20):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, it in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            r = p.add_run()
            r.text = "\u2022 " + it
            r.font.size, r.font.color.rgb = Pt(size), GREY
            p.space_after = Pt(10)

    def picture(slide, img, left, top, max_w, max_h):
        w, h = Image.open(img).size
        scale = min(max_w / w, max_h / h)
        slide.shapes.add_picture(img, Inches(left), Inches(top), Inches(w * scale), Inches(h * scale))

    def add(title, items=None, image=None):
        s = prs.slides.add_slide(blank)
        band(s, title)
        if image and os.path.exists(image):
            bullets_box(s, items or [], 0.6, 1.5, 6.2, 5.6)
            picture(s, image, 7.1, 1.5, 5.7, 5.5)
        else:
            bullets_box(s, items or [], 0.6, 1.5, 12.1, 5.6)
        return s

    # 1 Title
    s = prs.slides.add_slide(blank)
    band(s, "ReviewSense", height=7.5, size=54)
    bullets_box(s, ["Multi-Aspect Product Review & Customer Sentiment Hub", "Group D: Atik Hussain, Biki Sharmah, "
                    "Simran Saikia, Manoj"], 0.6, 4.6, 12, 2, size=24)
    for p in s.shapes[-1].text_frame.paragraphs:
        for r in p.runs:
            r.font.color.rgb = WHITE
    # 2-3
    add("Problem", ["Online shops get thousands of reviews; nobody can read them all",
                    "Star ratings hide what customers are unhappy about",
                    "We need fast sentiment plus the topic: quality, shipping or price"])
    add("Objectives", ["Predict sentiment: positive, neutral or negative",
                       "Tag aspects: Quality, Shipping, Price",
                       "Simple web page: one review in, result out",
                       "Measure with Macro-F1, Weighted-F1 and a confusion matrix"])
    # 4 Dataset
    items = [f"{DATASET_NAME}", f"Labels from rating: {LABEL_RULE}"]
    if facts["n_rows"]:
        items += [f"{facts['n_rows']:,} reviews used", _dist_text(facts)]
    add("Dataset", items, os.path.join(OUT_DIR, "class_distribution.png"))
    # 5-6
    app_items = ["Review text -> Streamlit page", "predict(text) loads the saved Joblib model",
                 "Aspect rules run on the same text", "Output: sentiment + aspect tags"]
    if HAS_FASTAPI:
        app_items.insert(2, "Optional FastAPI endpoint for batch requests")
    add("Architecture", app_items)
    add("Sentiment Model", [MODEL_NAME, "TF-IDF turns text into weighted word counts",
                            "Logistic Regression learns which words signal each class",
                            "Trained on a training split, scored on a held-out test set"])
    # 7 Aspects
    ex = "Good quality but delivery was late"
    add("Aspect Detection", ["Rule-based: whole-word keyword matching",
                             "One review can have several aspects, or none",
                             f"Example: \"{ex}\" -> {', '.join(detect_aspects(ex))}",
                             "Limit: shows the topic, not the sentiment about it"])
    # 8 Evaluation
    m = facts["metrics"]
    ev = []
    if m:
        ev = [f"Macro-F1: {m['macro_f1']:.3f}", f"Weighted-F1: {m['weighted_f1']:.3f}",
              f"Accuracy: {m['accuracy']:.3f}", f"Test reviews: {facts['n_test']:,}",
              "Macro-F1 is the main metric: classes are imbalanced"]
    add("Evaluation", ev, os.path.join(OUT_DIR, "confusion_matrix.png"))
    # 9 Demo + screenshots
    add("Live Demo", ["Positive review -> sentiment card", "\"Good quality but late delivery\" -> 2 aspects",
                      "One-word review -> no aspect"] + (["Upload CSV -> table and charts"] if HAS_CSV_BATCH else []))
    for shot in _screenshots():
        s = prs.slides.add_slide(blank)
        band(s, "Screenshot: " + os.path.splitext(os.path.basename(shot))[0].replace("_", " "), height=1.0, size=26)
        picture(s, shot, 1.2, 1.2, 10.9, 6.0)
    # 10 Testing table
    s = prs.slides.add_slide(blank)
    band(s, f"Testing: {rep['a_pass']}/{rep['a_total']} aspect tests passed"
         + (f", {rep['s_pass']}/{rep['s_total']} sentiment" if rep["s_total"] else ""))
    rows = rep["rows"][:11]
    tbl = s.shapes.add_table(len(rows) + 1, 4, Inches(0.6), Inches(1.5), Inches(12.1), Inches(0.4 * (len(rows) + 1))).table
    for j, h in enumerate(["Type", "Input", "Expected", "Actual / Result"]):
        tbl.cell(0, j).text = h
    for i, (kind, text, exp, got, res) in enumerate(rows, start=1):
        for j, v in enumerate([kind, text, exp, f"{got} ({res})"]):
            tbl.cell(i, j).text = v
    for r in tbl.rows:
        for c in r.cells:
            for p in c.text_frame.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(12)
    # 11-12
    add("Limitations & Future Work", ["Keyword rules miss synonyms, sarcasm and negation",
                                      "Neutral reviews are the hardest class for TF-IDF models",
                                      "Future: BERT-style model, aspect-level sentiment, more languages"])
    add("Conclusion & Q&A", ["Working pipeline: review in, sentiment and aspects out",
                             "Evaluated with Macro-F1, Weighted-F1 and a confusion matrix",
                             "Thank you. Questions?"])
    prs.save(path)
    print(f"Saved {path} ({len(prs.slides)} slides)")
    if facts["missing"]:
        print("Some slides have no numbers because:")
        for mm in facts["missing"]:
            print("  -", mm)


# =====================================================================================
# STREAMLIT DEMO PAGE + MAIN
# =====================================================================================
def _streamlit_page():
    """streamlit run simran_all_in_one.py -> demo dashboard (CSV upload)."""
    import pandas as pd
    import streamlit as st
    st.title("ReviewSense - Analytics Dashboard")
    up = st.file_uploader("Results CSV (review text + sentiment)", type="csv")
    if up:
        df = pd.read_csv(up)
        try:
            _first_col(df, TEXT_CANDIDATES, "review text")
            _first_col(df, SENTIMENT_CANDIDATES, "sentiment")
        except KeyError as e:
            st.error(str(e))
        else:
            show_dashboard(df)


def demo_aspects():
    for t in ["Great quality but delivery was late", "Too expensive", "Nice", ""]:
        print(repr(t), "->", detect_aspects(t))


def run_all():
    steps = [("eda", run_eda), ("eval", run_eval), ("charts", run_charts), ("test", run_tests),
             ("docs", make_docs), ("ppt", make_ppt)]
    status = []
    for name, fn in steps:
        print(f"\n===== {name} =====")
        try:
            fn()
            status.append((name, "ok"))
        except Exception as e:
            print(f"!! {name} failed: {type(e).__name__}: {e}")
            status.append((name, f"FAILED: {type(e).__name__}: {e}"))
    print("\n===== summary =====")
    for n, s in status:
        print(f"{n:8} {s}")


def _in_streamlit():
    try:
        from streamlit.runtime import exists
        return exists()
    except Exception:
        return False


if __name__ == "__main__":
    ACTIONS = {"all": run_all, "eda": run_eda, "aspects": demo_aspects, "coverage": run_coverage,
               "eval": run_eval, "charts": run_charts, "test": run_tests, "docs": make_docs,
               "ppt": make_ppt}
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd in ACTIONS:
        ACTIONS[cmd]()
    elif cmd == "" and _in_streamlit():
        _streamlit_page()
    else:
        if cmd:
            print("Unknown command:", cmd)
        print(__doc__)