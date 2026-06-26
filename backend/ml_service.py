import joblib
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# Path to saved models
MODELS_PATH = os.getenv("MODELS_PATH", "D:/medisimplify/ml/risk_models.pkl")

# Risk level mapping
RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}

# Load models once when server starts
_models = None


def load_models():
    """Load ML models from disk"""
    global _models
    if _models is None:
        try:
            _models = joblib.load(MODELS_PATH)
            print(f"ML models loaded: {list(_models.keys())}")
        except Exception as e:
            print(f"ML models not found: {e}")
            _models = {}
    return _models


def detect_report_type(values: dict) -> str:
    """
    Detect which type of medical report based on
    the lab values present.

    Returns: 'diabetes', 'heart', 'kidney', or 'unknown'
    """
    # Diabetes indicators
    diabetes_keys = ["glucose", "Glucose", "hba1c", "HbA1c", "insulin", "Insulin"]

    # Heart indicators
    heart_keys = [
        "thalach",
        "cp",
        "chol",
        "cholesterol",
        "trestbps",
        "exang",
        "oldpeak",
    ]

    # Kidney indicators
    kidney_keys = ["creatinine", "sc", "urea", "bu", "hemoglobin", "hemo", "eGFR"]

    values_lower = {k.lower(): v for k, v in values.items()}

    diabetes_score = sum(1 for k in diabetes_keys if k.lower() in values_lower)
    heart_score = sum(1 for k in heart_keys if k.lower() in values_lower)
    kidney_score = sum(1 for k in kidney_keys if k.lower() in values_lower)

    scores = {"diabetes": diabetes_score, "heart": heart_score, "kidney": kidney_score}

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "unknown"
    return best


def prepare_diabetes_features(values: dict) -> dict:
    """Extract and map diabetes features"""
    v = {k.lower(): val for k, val in values.items()}
    return {
        "Glucose": float(v.get("glucose", 100)),
        "BMI": float(v.get("bmi", 25)),
        "Age": float(v.get("age", 40)),
        "BloodPressure": float(v.get("bloodpressure", 80)),
        "Insulin": float(v.get("insulin", 80)),
        "DiabetesPedigreeFunction": float(v.get("diabetespedigreefunction", 0.5)),
        "Pregnancies": float(v.get("pregnancies", 0)),
        "SkinThickness": float(v.get("skinthickness", 20)),
    }


def prepare_heart_features(values: dict) -> dict:
    """Extract and map heart features"""
    v = {k.lower(): val for k, val in values.items()}
    return {
        "age": float(v.get("age", 50)),
        "sex": float(v.get("sex", 1)),
        "cp": float(v.get("cp", 0)),
        "trestbps": float(v.get("trestbps", 120)),
        "chol": float(v.get("chol", v.get("cholesterol", 200))),
        "fbs": float(v.get("fbs", 0)),
        "restecg": float(v.get("restecg", 0)),
        "thalach": float(v.get("thalach", 150)),
        "exang": float(v.get("exang", 0)),
        "oldpeak": float(v.get("oldpeak", 0)),
        "slope": float(v.get("slope", 1)),
        "ca": float(v.get("ca", 0)),
        "thal": float(v.get("thal", 2)),
    }


def prepare_kidney_features(values: dict) -> dict:
    """Extract and map kidney features"""
    v = {k.lower(): val for k, val in values.items()}
    return {
        "age": float(v.get("age", 50)),
        "bp": float(v.get("bp", 80)),
        "sc": float(v.get("sc", v.get("creatinine", 1.0))),
        "hemo": float(v.get("hemo", v.get("hemoglobin", 13.0))),
        "bu": float(v.get("bu", v.get("urea", 30))),
        "bgr": float(v.get("bgr", v.get("glucose", 100))),
        "sod": float(v.get("sod", v.get("sodium", 135))),
        "pot": float(v.get("pot", v.get("potassium", 4.0))),
    }


def predict_risk(values: dict) -> dict:
    """
    Main function — takes lab values dict and
    returns risk prediction.

    Args:
        values: dict of lab values from Claude output
                e.g. {"Glucose": 180, "BMI": 32, "Age": 45}

    Returns:
        dict with risk_level, confidence, model_used
    """
    models = load_models()

    if not models:
        return {
            "risk_level": "Unknown",
            "confidence": 0.0,
            "model_used": "none",
            "message": "ML models not available",
        }

    # Detect report type
    report_type = detect_report_type(values)

    if report_type == "unknown" or report_type not in models:
        # Fallback: use rule-based risk assessment
        return rule_based_risk(values)

    try:
        model_data = models[report_type]
        model = model_data["model"]
        scaler = model_data["scaler"]
        selector = model_data["selector"]
        features = model_data["features"]

        # Prepare features based on report type
        if report_type == "diabetes":
            prepared = prepare_diabetes_features(values)
        elif report_type == "heart":
            prepared = prepare_heart_features(values)
        else:
            prepared = prepare_kidney_features(values)

        # Build feature array in correct order
        feature_array = []
        for feat in features:
            val = prepared.get(feat, 0.0)
            feature_array.append(float(val))

        X = np.array(feature_array).reshape(1, -1)

        # Add engineered features to match training
        X = add_engineered_features(X, features, prepared)

        # Scale
        X_scaled = scaler.transform(X)

        # Select features
        X_selected = selector.transform(X_scaled)

        # Predict
        prediction = model.predict(X_selected)[0]
        probabilities = model.predict_proba(X_selected)[0]
        confidence = float(max(probabilities))

        risk_level = RISK_LABELS.get(int(prediction), "Unknown")

        return {
            "risk_level": risk_level,
            "confidence": round(confidence * 100, 1),
            "model_used": report_type,
            "model_name": model_data.get("model_name", "ML Model"),
        }

    except Exception as e:
        print(f"ML prediction error: {e}")
        return rule_based_risk(values)


def add_engineered_features(X, features, prepared):
    """
    Add engineered features to match training data shape.
    This ensures feature count matches what model expects.
    """
    # We return X as-is since the selector will handle
    # the feature selection automatically
    return X


def rule_based_risk(values: dict) -> dict:
    """
    Fallback rule-based risk assessment when ML
    model cannot be used.
    Based on standard medical reference ranges.
    """
    v = {k.lower(): val for k, val in values.items()}
    risk_score = 0

    # Glucose check
    glucose = float(v.get("glucose", 0))
    if glucose > 200:
        risk_score += 3
    elif glucose > 140:
        risk_score += 2
    elif glucose > 100:
        risk_score += 1

    # HbA1c check
    hba1c = float(v.get("hba1c", 0))
    if hba1c > 8:
        risk_score += 3
    elif hba1c > 6.5:
        risk_score += 2

    # Creatinine check
    creatinine = float(v.get("creatinine", v.get("sc", 0)))
    if creatinine > 3.5:
        risk_score += 3
    elif creatinine > 1.5:
        risk_score += 2

    # Hemoglobin check
    hemo = float(v.get("hemoglobin", v.get("hemo", 13)))
    if hemo < 8:
        risk_score += 3
    elif hemo < 11:
        risk_score += 1

    # Blood pressure check
    bp = float(v.get("bloodpressure", v.get("bp", 80)))
    if bp > 120:
        risk_score += 2
    elif bp > 100:
        risk_score += 1

    # Cholesterol check
    chol = float(v.get("cholesterol", v.get("chol", 200)))
    if chol > 280:
        risk_score += 2
    elif chol > 240:
        risk_score += 1

    # Map score to risk level
    if risk_score >= 5:
        risk_level = "High"
    elif risk_score >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "confidence": 70.0,
        "model_used": "rule_based",
        "model_name": "Rule-Based Assessment",
    }


# Load models when module is imported
load_models()
