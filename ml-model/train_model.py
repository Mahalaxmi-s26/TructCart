import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_excel(
    r"D:\MCA 2nd sem\TrustCart\dataset\merged_electronics_dataset.xlsx"
)
# Encoding
le_material = LabelEncoder()
le_power = LabelEncoder()
le_recyclable = LabelEncoder()
le_carbon = LabelEncoder()
le_target = LabelEncoder()

data['material'] = le_material.fit_transform(data['material'])
data['power_usage'] = le_power.fit_transform(data['power_usage'])
data['recyclable'] = le_recyclable.fit_transform(data['recyclable'])
data['carbon_footprint'] = le_carbon.fit_transform(data['carbon_footprint'])
data['eco_friendly'] = le_target.fit_transform(data['eco_friendly'])

# Features
X = data[['material', 'power_usage', 'recyclable', 'carbon_footprint']]

# Target
y = data['eco_friendly']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Train
model = RandomForestClassifier()

model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print("Accuracy:", accuracy)

# Save model
joblib.dump(model, "eco_model.pkl")

print("Model saved successfully")