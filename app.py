"""
Organic / Inorganic Product Classifier
Flask backend — trains on merged_products_final.xlsx
"""

import os, json, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import joblib

# ─── Material classification rules ────────────────────────────────────────────

ORGANIC_MATERIALS = {
   "beeswax", "bamboo", "wood",
    "biodegradable", "hemp", "jute", "linen", "wool", "cork", "paper",
    "charcoal", "plant", "organic", "cellulose", "coconut", "compostable",
    "botanical", "herbal", "seed", "vegetable", "fruit", "grain", "clay",
    "earth", "rubber", "beeswax", "straw", "cane", "rattan", "sisal",
    "flax", "kenaf", "abaca", "kapok", "seagrass", "moss", "mycelium"
}

INORGANIC_MATERIALS = {
    "plastic", "silicone", "metal", "glass", "aluminum", "aluminium",
    "steel", "iron", "copper", "nylon", "polyester", "acrylic",
    "fiberglass", "ceramic", "synthetic", "chemical", "polymer", "resin",
    "foam", "carbon fiber", "stainless steel", "stainless", "cast iron",
    "brass", "zinc", "chrome", "titanium", "pvc", "abs", "polypropylene",
    "polyethylene", "polycarbonate", "latex", "microfiber", "fleece",
    "spandex", "lycra", "rayon", "viscose", "recycled plastic",
    "plastic/glass", "metal/glass", "metal/plastic"
}

MIXED_MATERIALS = {
    "mixed/other", "plastic/glass", "metal/glass", "metal/plastic",
    "composite", "mixed", "combination"
}


def classify_by_material(material: str) -> str:
    """Strict rule-based classification from material string."""
    if not material or str(material).strip().lower() in ("nan", "none", ""):
        return "Unknown"

    m = str(material).strip().lower()

    # Direct exact match wins immediately
    for w in INORGANIC_MATERIALS:
        if w == m or m.startswith(w):
            return "Inorganic"
    for w in ORGANIC_MATERIALS:
        if w == m or m.startswith(w):
            return "Organic"

    # Check mixed
    for w in MIXED_MATERIALS:
        if w in m:
            return "Mixed"

    # Substring scoring
    org_score   = sum(1 for w in ORGANIC_MATERIALS   if w in m)
    inorg_score = sum(1 for w in INORGANIC_MATERIALS if w in m)

    if inorg_score > 0 and inorg_score >= org_score: return "Inorganic"
    if org_score   > 0 and org_score  >  inorg_score: return "Organic"
    if org_score == inorg_score > 0: return "Mixed"
    return "Unknown"


# ─── Load & prepare dataset ───────────────────────────────────────────────────

def load_dataset(path="merged_products_final.xlsx"):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["material"]     = df["material"].fillna("Unknown")
    df["product_name"] = df["product_name"].fillna("")
    df["category"]     = df["category"].fillna("Unknown")

    df["classification"] = df["material"].apply(classify_by_material)

    # Stats
    counts = df["classification"].value_counts().to_dict()
    mat_counts = df.groupby(["classification","material"]).size().reset_index(name="count")

    return df, counts, mat_counts


# ─── ML Model ────────────────────────────────────────────────────────────────

class Classifier:
    def __init__(self):
        self.pipeline = None
        self.le       = LabelEncoder()
        self.accuracy = 0.0

    def train(self, df):
        print("Training ML classifier…")
        known = df[df["classification"] != "Unknown"].copy()
        X = known["product_name"] + " " + known["material"] + " " + known["category"]
        y = self.le.fit_transform(known["classification"])

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1,2))),
            ("clf",   RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
        ])
        cv = cross_val_score(self.pipeline, X, y, cv=5, scoring="accuracy")
        self.pipeline.fit(X, y)
        self.accuracy = round(cv.mean() * 100, 1)
        print(f"  ✅ Accuracy: {self.accuracy}%")

    def predict(self, product_name: str, material: str = "", category: str = "") -> dict:
        # Rule-based from material — always takes priority
        rule = classify_by_material(material) if material else "Unknown"

        # Also scan product name for material clues if rule is Unknown
        name_rule = classify_by_material(product_name) if rule == "Unknown" else "Unknown"

        # ML prediction
        text = f"{product_name} {material} {category}"
        proba = self.pipeline.predict_proba([text])[0]
        pred_idx = int(np.argmax(proba))
        ml_label = self.le.inverse_transform([pred_idx])[0]
        confidence = round(float(proba[pred_idx]) * 100)

        # Decision priority: rule > name_rule > ML
        if rule != "Unknown":
            final = rule
        elif name_rule != "Unknown":
            final = name_rule
        else:
            final = ml_label

        return {
            "classification": final,
            "ml_label":       ml_label,
            "rule_label":     rule if rule != "Unknown" else name_rule,
            "confidence":     confidence,
            "material":       material or "Not specified",
        }

    def save(self, path="models/classifier.pkl"):
        os.makedirs("models", exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path="models/classifier.pkl"):
        return joblib.load(path)


# ─── Flask app ────────────────────────────────────────────────────────────────

def run():
    from flask import Flask, jsonify, request, send_from_directory
    app = Flask(__name__, static_folder="ui", static_url_path="")

    print("Loading dataset…")
    df, counts, mat_counts = load_dataset()

    clf = Classifier()
    clf.train(df)

    # Pre-build summary stats for the dashboard
    category_breakdown = (
        df[df["classification"] != "Unknown"]
        .groupby(["category", "classification"])
        .size()
        .reset_index(name="count")
        .to_dict(orient="records")
    )

    material_breakdown = (
        df.groupby(["material", "classification"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(30)
        .to_dict(orient="records")
    )

    @app.route("/")
    def index():
        return send_from_directory("ui", "index.html")

    @app.route("/api/stats")
    def stats():
        return jsonify({
            "total":        int(len(df)),
            "organic":      int(counts.get("Organic", 0)),
            "inorganic":    int(counts.get("Inorganic", 0)),
            "mixed":        int(counts.get("Mixed", 0)),
            "unknown":      int(counts.get("Unknown", 0)),
            "accuracy":     clf.accuracy,
            "categories":   category_breakdown,
            "materials":    material_breakdown,
        })

    @app.route("/api/classify", methods=["POST"])
    def classify():
        data = request.get_json(silent=True) or {}
        print(f"Received request: {data}")

        name = str(data.get("product", "")).strip()
        material = str(data.get("material", "")).strip()

        # Validate required fields
        if not name:
            return jsonify({"error": "Product name is required"}), 400

        if not material:
            return jsonify({"error": "Material is required"}), 400

        result = clf.predict(name, material)
        return jsonify(result)
    @app.route("/api/products")
    def products():
        q    = request.args.get("q","").lower()
        cls  = request.args.get("cls","")
        cat  = request.args.get("cat","")
        page = int(request.args.get("page", 1))
        per  = 20
        filt = df.copy()
        if q:   filt = filt[filt["product_name"].str.lower().str.contains(q, na=False)]
        if cls: filt = filt[filt["classification"] == cls]
        if cat: filt = filt[filt["category"] == cat]
        total = len(filt)
        chunk = filt.iloc[(page-1)*per : page*per]
        rows  = chunk[["product_name","material","category","classification","ratings","eco_score"]].to_dict(orient="records")
        return jsonify({"total": total, "page": page, "per": per, "rows": rows})

    @app.route("/api/categories")
    def categories():
        return jsonify(sorted(df["category"].dropna().unique().tolist()))

    import webbrowser, threading
    port = 5055
    threading.Timer(1.2, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    print(f"\n🌐  Open http://localhost:{port}\n    Ctrl+C to stop.\n")
    return app


app = run()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
