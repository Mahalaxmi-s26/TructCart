import pickle
import re

# LOAD MODEL
with open("model/trustcart_model.pkl", "rb") as f:
    model = pickle.load(f)

# LOAD VECTORIZER
with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# TEXT CLEANING (same style as training)
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

# USER INPUT
while True:
    review = input("\nEnter a review (or type 'exit'): ")

    if review.lower() == "exit":
        break

    cleaned = clean_text(review)

    vector = vectorizer.transform([cleaned])

    prediction = model.predict(vector)

    print("Prediction:", prediction[0])