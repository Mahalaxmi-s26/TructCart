from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load trained model
model = joblib.load("eco_model.pkl")

@app.route('/predict', methods=['POST'])

def predict():

    try:

        data = request.json

        material = int(data['material'])
        power_usage = int(data['power_usage'])
        recyclable = int(data['recyclable'])
        carbon = int(data['carbon_footprint'])

        features = np.array([[
            material,
            power_usage,
            recyclable,
            carbon
        ]])

        prediction = model.predict(features)

        result = (
            "Eco Friendly"
            if prediction[0] == 1
            else "Not Eco Friendly"
        )

        eco_score = 85 if prediction[0] == 1 else 35

        explanation = ""

        if prediction[0] == 1:

            explanation = (
                "This product is environmentally friendly "
                "because it uses sustainable materials "
                "and has lower carbon emissions."
            )

        else:

            explanation = (
                "This product may negatively affect the "
                "environment due to higher emissions "
                "and non-recyclable materials."
            )

        return jsonify({

            "prediction": result,

            "eco_score": eco_score,

            "explanation": explanation
        })

    except Exception as e:

        print(e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':

    app.run(debug=True)