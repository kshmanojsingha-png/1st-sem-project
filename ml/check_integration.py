import joblib
import pandas as pd
from ml.predictor import predict, MODEL_PATH

REVIEWS = [
    "Absolutely loved it, great taste and fresh.",
    "Terrible. It arrived broken and tasted awful.",
    "It was okay, nothing special.",
    "Not good at all, I will never buy this again.",
    "Not bad, though a bit pricey for what you get.",
    "Delivery was slow but the product itself is excellent.",
]

direct = joblib.load(MODEL_PATH).predict(REVIEWS)
shared = predict(REVIEWS)

df = pd.DataFrame({"review": REVIEWS,
                   "direct_model": direct,
                   "predict_function": shared})
df["match"] = df["direct_model"] == df["predict_function"]
print(df.to_string(index=False))
print("\nAll match:", df["match"].all())
df.to_csv("outputs/integration_check.csv", index=False)

# Input validation checks
for bad in ([], [""], ["   "]):
    try:
        predict(bad)
        print("NOT rejected:", bad)
    except ValueError as e:
        print("Rejected correctly:", repr(bad), "->", e)