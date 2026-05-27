from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load model
model = joblib.load("eco_model.pkl")


@app.route('/predict', methods=['POST'])
def predict():

    try:

        data = request.get_json()

        # Convert safely to integers

        material = int(data.get('material', 0))
        power_usage = int(data.get('power_usage', 0))
        recyclable = int(data.get('recyclable', 0))
        carbon = int(data.get('carbon_footprint', 0))

        # Create feature array

        features = np.array([[
            material,
            power_usage,
            recyclable,
            carbon
        ]])

        # Prediction

        prediction = model.predict(features)

        result = (
            "Eco Friendly"
            if prediction[0] == 1
            else "Not Eco Friendly"
        )

        eco_score = 85 if prediction[0] == 1 else 35

        # Explanation

        if prediction[0] == 1:

            explanation = (
                "This product is environmentally friendly "
                "because it uses sustainable materials "
                "and lower carbon emissions."
            )

        else:

            explanation = (
                "This product may negatively affect "
                "the environment due to higher emissions "
                "and non-recyclable materials."
            )

        return jsonify({

            "prediction": result,
            "eco_score": eco_score,
            "explanation": explanation

        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':

    app.run(debug=True)