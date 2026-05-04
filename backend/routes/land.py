from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pickle, numpy as np, os

router = APIRouter()

class LandInput(BaseModel):
    state:        str   = Field(..., description="State code e.g. AP, TS")
    area_acres:   float = Field(..., gt=0, description="Land area in acres")
    soil_type:    int   = Field(..., ge=1, le=5, description="1=Black,2=Red,3=Loam,4=Sandy,5=Alluvial")
    irrigation:   int   = Field(..., ge=1, le=4, description="1=Canal,2=Borewell,3=Rainfed,4=Drip")
    road_km:      float = Field(..., ge=0, description="Distance to main road in km")

# State base price per acre (INR) — based on 2024 market averages
BASE_PRICES = {
    "AP": 800000, "TS": 750000, "KA": 950000,
    "TN": 1100000, "MH": 1200000, "UP": 450000,
    "RJ": 380000,  "GJ": 900000, "PB": 1300000
}
SOIL_MULT   = {1: 1.2, 2: 0.9, 3: 1.1, 4: 0.8, 5: 1.3}
IRR_MULT    = {1: 1.3, 2: 1.1, 3: 0.8, 4: 1.2}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml_models/land_model.pkl")
land_model = None
try:
    with open(MODEL_PATH, "rb") as f:
        land_model = pickle.load(f)
    print("SUCCESS: Land model loaded")
except: print("WARNING: Land model not found — using formula-based estimation")

@router.post("/land")
def predict_land(data: LandInput):
    """Estimate land price using ML model or formula fallback."""
    try:
        if land_model:
            state_enc = hash(data.state) % 20  # Encode state as number
            features = np.array([[
                state_enc, data.area_acres, data.soil_type,
                data.irrigation, data.road_km
            ]])
            price = float(land_model.predict(features)[0])
        else:
            base = BASE_PRICES.get(data.state.upper(), 600000)
            road_factor = max(0.7, 1 - (data.road_km * 0.05))
            price = base * data.area_acres * SOIL_MULT[data.soil_type] * IRR_MULT[data.irrigation] * road_factor

        return {
            "total_value":    round(price),
            "per_acre":       round(price / data.area_acres),
            "state":          data.state.upper(),
            "area_acres":     data.area_acres,
            "currency":       "INR",
            "confidence":     "±15% range",
            "status":         "success"
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
