import pandas as pd
from sklearn.model_selection import train_test_split

DATA_PATH = "data/Reviews.csv"

def to_label(score):
    if score <= 2:
        return "negative"
    elif score == 3:
        return "neutral"
    return "positive"

def load_split():
    df = pd.read_csv(DATA_PATH, usecols=["Text", "Score"])
    df = df.dropna().drop_duplicates(subset="Text")
    df["label"] = df["Score"].apply(to_label)
    df = df.sample(n=30000, random_state=42)
    return train_test_split(df["Text"], df["label"], test_size=0.2,
                            stratify=df["label"], random_state=42)