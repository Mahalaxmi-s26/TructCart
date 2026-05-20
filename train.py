import pandas as pd
import re
import pickle
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# LOAD DATA
df = pd.read_csv("dataset/final_narratives.csv")

print("ORIGINAL SIZE:", len(df))

# FIX 1: CLEAN RATING COLUMN
def extract_rating(text):
    match = re.search(r"([0-9.]+)", str(text))
    if match:
        return float(match.group(1))
    return None

df["review_rating"] = df["review_rating"].apply(extract_rating)

df = df.dropna(subset=["review_rating"])

print("AFTER RATING CLEAN:", len(df))


# TEXT COLUMN

TEXT_COLUMN = "raw_best_summary"

df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str)
df = df[df[TEXT_COLUMN].str.strip().str.len() > 5]

print("AFTER TEXT CLEAN:", len(df))


# LABEL CREATION

df["label"] = df["review_rating"].apply(
    lambda x: "positive" if x >= 4 else "negative"
)

label_counts = df["label"].value_counts()

plt.figure()
label_counts.plot(kind="bar")
plt.title("Sentiment Distribution (Positive vs Negative)")
plt.xlabel("Sentiment")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# BALANCE DATASET (SAFE)

balanced_df = []

for label in df["label"].unique():
    temp = df[df["label"] == label]
    balanced_df.append(temp.sample(min(len(temp), 1500), random_state=42))

df = pd.concat(balanced_df).reset_index(drop=True)

print("AFTER BALANCING:", len(df))


# FEATURES & LABELS

X = df[TEXT_COLUMN]
y = df["label"]


# TF-IDF VECTORIZATION

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=8000,
    ngram_range=(1, 2)
)

X_vectorized = vectorizer.fit_transform(X)


# TRAIN TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42
)


# MODEL

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# EVALUATION

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nACCURACY:", accuracy * 100)

plt.figure()

plt.bar(["Model Accuracy"], [accuracy * 100])

plt.ylim(0, 100)

plt.title("Model Accuracy")

plt.ylabel("Accuracy %")

plt.show()
# SAVE MODEL

with open("model/trustcart_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\nMODEL SAVED SUCCESSFULLY")