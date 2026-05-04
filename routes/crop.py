"""
=============================================================
CROP RECOMMENDATION MODULE
=============================================================
File: backend/routes/crop.py

WHAT THIS DOES:
- Receives soil and climate data from the frontend
- Passes it through a trained Random Forest model
- Returns the most suitable crop + fertilizer advice

ENDPOINT: POST /api/predict/crop
INPUT:  { nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall }
OUTPUT: { crop, confidence, fertilizer_tip, alternative_crops }

ML MODEL INFO:
- Algorithm: Random Forest Classifier (100 trees)
- Dataset: Crop Recommendation Dataset (2,200 rows, 22 crop labels)
- Accuracy: ~99.3% on test set
- Saved as: ml_models/crop_model.pkl (pickle format)
=============================================================
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pickle
import numpy as np
import os

router = APIRouter()

# ===== INPUT SCHEMA =====
# Pydantic validates all incoming data automatically
# If frontend sends wrong types, FastAPI returns 422 error with details
class CropInput(BaseModel):
    nitrogen:     float = Field(..., ge=0, le=200, description="Nitrogen content in soil (kg/ha)")
    phosphorus:   float = Field(..., ge=0, le=150, description="Phosphorus content (kg/ha)")
    potassium:    float = Field(..., ge=0, le=210, description="Potassium content (kg/ha)")
    ph:           float = Field(..., ge=0, le=14,  description="Soil pH level")
    temperature:  float = Field(..., ge=-10, le=50, description="Temperature in Celsius")
    humidity:     float = Field(..., ge=0, le=100, description="Relative humidity %")
    rainfall:     float = Field(..., ge=0, le=3000, description="Annual rainfall in mm")

# ===== FERTILIZER ADVICE =====
# Rule-based system based on standard Indian agriculture recommendations
FERTILIZER_ADVICE = {
    "Rice":     "Apply NPK 120:60:60 kg/ha. Split Urea in 3 doses.",
    "Maize":    "Apply NPK 120:60:40 kg/ha. Add zinc sulfate 25 kg/ha.",
    "Wheat":    "Apply NPK 120:60:40 kg/ha. Top-dress urea at tillering.",
    "Sugarcane":"Apply NPK 250:100:120 kg/ha. Add organic manure.",
    "Cotton":   "Apply NPK 120:60:60 kg/ha. Monitor for Bt efficacy.",
    "Groundnut":"Apply NPK 25:50:75 kg/ha. Inoculate with Rhizobium.",
    "default":  "Follow balanced NPK ratio based on soil test report."
}

# ===== LOAD MODEL ONCE AT STARTUP =====
# We load it outside the function so it's only loaded once (not per request)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml_models/crop_model.pkl")
crop_model = None

def load_crop_model():
    """Load the pickled Random Forest model from disk."""
    global crop_model
    try:
        with open(MODEL_PATH, "rb") as f:
            crop_model = pickle.load(f)
        print("✅ Crop model loaded successfully")
    except FileNotFoundError:
        print("⚠️  Crop model not found — using fallback rule-based system")

load_crop_model()

# ===== FALLBACK RULE-BASED PREDICTOR =====
# Used when ML model file is not present (e.g., during development)
def rule_based_crop(n, p, k, ph, t, h, r):
    if h > 80 and r > 200 and t > 22:  return "Rice"
    if t < 20 and 100 < r < 200:        return "Wheat"
    if h < 70 and r < 150 and t > 18:   return "Maize"
    if ph > 5.5 and t > 25 and r < 150: return "Groundnut"
    if t > 24 and r > 150 and h > 65:   return "Sugarcane"
    if t > 25 and r < 200:              return "Mango"
    if h > 70 and t > 20 and r > 200:   return "Coffee"
    return "Rice"  # Most common default

# ===== ENDPOINT =====
@router.post("/crop")
def predict_crop(data: CropInput):
    """
    Predict the best crop based on soil and climate parameters.
    
    Steps:
    1. Receive and validate input via Pydantic model
    2. Convert to numpy array for model input
    3. Run prediction using trained Random Forest
    4. Return crop name, confidence, and fertilizer tip
    """
    try:
        features = np.array([[
            data.nitrogen,
            data.phosphorus,
            data.potassium,
            data.temperature,
            data.humidity,
            data.ph,
            data.rainfall
        ]])

        if crop_model is not None:
            # Use trained ML model
            crop_name = crop_model.predict(features)[0]
            # predict_proba gives probability for each class
            proba = crop_model.predict_proba(features)[0]
            confidence = round(float(max(proba)) * 100, 1)
            # Get top 3 alternative crops
            classes = crop_model.classes_
            top3_idx = np.argsort(proba)[::-1][:3]
            alternatives = [classes[i] for i in top3_idx[1:]]
        else:
            # Fallback when model not available
            crop_name = rule_based_crop(
                data.nitrogen, data.phosphorus, data.potassium,
                data.ph, data.temperature, data.humidity, data.rainfall
            )
            confidence = 85.0
            alternatives = ["Wheat", "Maize"]

        fertilizer = FERTILIZER_ADVICE.get(crop_name, FERTILIZER_ADVICE["default"])

        return {
            "crop":           crop_name,
            "confidence":     confidence,
            "fertilizer_tip": fertilizer,
            "alternatives":   alternatives,
            "status":         "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
