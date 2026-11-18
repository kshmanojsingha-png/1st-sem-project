# PPT Outline (12 slides + screenshots)
1 Title | 2 Problem | 3 Objectives | 4 Dataset + class chart | 5 Architecture | 6 Sentiment model
7 Aspect detection | 8 Evaluation (confusion matrix, F1) | 9 Live demo | (screenshots) | 10 Testing table | 11 Limitations & future work | 12 Conclusion / Q&A

# Demo script
1. Type a positive review -> sentiment shown
2. Type "Good quality but late delivery" -> two aspect tags (Quality, Shipping)
3. Type a one-word review ("Nice") -> no aspect
4. Upload a CSV -> results table + donut chart
5. Use the aspect filter "Shipping"
6. Download the results CSV
7. Upload a CSV with the wrong column -> friendly error message

# Theory Q&A
- **Why Macro-F1?** It treats every class equally, so a model cannot look good just by predicting the big class. Accuracy misleads on imbalanced data.
- **Macro vs Weighted F1?** Macro = plain average of the class F1 scores. Weighted = average weighted by how many reviews each class has.
- **What is a confusion matrix?** A table of actual vs predicted classes. The diagonal is correct predictions.
- **What is TF-IDF?** It turns text into numbers: words frequent in a review but rare across all reviews get a high weight.
- **Why Logistic Regression?** Fast, easy to explain, a strong baseline for text, and simple to save and load with Joblib.
- **How were labels made?** From the star rating: rating 1-2 = negative, 3 = neutral, 4-5 = positive.
- **How do you avoid leakage?** The test set is held out and never used for training. Check in train.py that TF-IDF is fitted on the training split only.
- **Why rule-based aspects?** Simple, explainable, needs no labelled aspect data, and fits the time limit.
- **Limitations?** Synonyms, sarcasm, negation; the neutral class is hardest; aspect tags show the topic, not the sentiment.
- **Several or no aspects?** A list is returned; the list is empty if nothing matches.
- **Future work?** BERT-style model, aspect-based sentiment, more languages.
