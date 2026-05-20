import pandas as pd
import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')

# Load cleaned dataset
df = pd.read_csv("dataset/final_narratives.csv")

# SHOW COLUMN NAMES
print(df.columns)

TEXT_COLUMN = "raw_best_summary"

# Initialize stemmer
stemmer = PorterStemmer()

# Load stopwords
stop_words = set(stopwords.words('english'))

# Text cleaning function
def preprocess_text(text):

    # Convert to string and lowercase
    text = str(text).lower()

    # Remove punctuation and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Split into words
    words = text.split()

    # Remove stopwords and apply stemming
    words = [
        stemmer.stem(word)
        for word in words
        if word not in stop_words
    ]

    # Join back into sentence
    return " ".join(words)

df = df.dropna()
# Apply preprocessing
df[TEXT_COLUMN] = df[TEXT_COLUMN].astype(str).apply(preprocess_text)

# Show processed text
print("\nPROCESSED DATA:\n")
print(df[TEXT_COLUMN].head())

# Save processed dataset
df.to_csv("dataset/preprocessed_final_narratives.csv", index=False)

print("\nPreprocessed dataset saved successfully.")