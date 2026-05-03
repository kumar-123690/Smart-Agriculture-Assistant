"""
=============================================================
LAND PRICE PREDICTION MODULE
=============================================================
File: backend/routes/land.py
ENDPOINT: POST /api/predict/land
"""
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
    print("✅ Land model loaded")
except: print("⚠️  Land model not found — using formula-based estimation")

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


"""
=============================================================
WEATHER MODULE
=============================================================
File: backend/routes/weather.py (combined here for brevity)
ENDPOINT: GET /api/weather?city=Kurnool
"""
from fastapi import Query
import httpx

weather_router = APIRouter()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")

@weather_router.get("/")
async def get_weather(city: str = Query(..., description="City name")):
    """
    Fetch real-time weather from OpenWeatherMap API.
    
    HOW TO GET API KEY:
    1. Sign up free at https://openweathermap.org/api
    2. Copy your API key
    3. Set env variable: export OPENWEATHER_API_KEY=your_key
    4. Or set it in .env file: OPENWEATHER_API_KEY=your_key
    """
    if WEATHER_API_KEY == "your_api_key_here":
        # Return demo data when no API key configured
        return {
            "city": city,
            "temperature": 32,
            "feels_like": 36,
            "humidity": 65,
            "wind_speed": 14,
            "description": "Partly Cloudy",
            "rain_chance": 30,
            "farming_advisory": "Moderate humidity — good for most field crops. Irrigate if needed.",
            "note": "Demo data — add OPENWEATHER_API_KEY env variable for live data",
            "status": "demo"
        }

    try:
        async with httpx.AsyncClient() as client:
            # Current weather
            resp = await client.get(
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
            )
            resp.raise_for_status()
            d = resp.json()

            # 5-day forecast for rain chance
            f_resp = await client.get(
                f"https://api.openweathermap.org/data/2.5/forecast"
                f"?q={city}&appid={WEATHER_API_KEY}&units=metric&cnt=8"
            )
            forecast = f_resp.json()
            rain_chance = int(forecast["list"][0].get("pop", 0) * 100)

        temp = round(d["main"]["temp"])
        humidity = d["main"]["humidity"]

        # Generate context-aware farming advisory
        if rain_chance > 60:
            advisory = "🌧️ Rain likely — delay pesticide/fertilizer application. Good time for transplanting."
        elif temp > 38:
            advisory = "🌡️ Extreme heat — irrigate early morning (before 8AM) or evening. Watch for heat stress."
        elif humidity > 85:
            advisory = "💧 High humidity — fungal disease risk elevated. Inspect crops and improve air circulation."
        else:
            advisory = "✅ Favorable conditions for field operations. Good day for harvesting and sowing."

        return {
            "city":             d["name"],
            "temperature":      temp,
            "feels_like":       round(d["main"]["feels_like"]),
            "humidity":         humidity,
            "wind_speed":       round(d["wind"]["speed"] * 3.6, 1),  # m/s → km/h
            "description":      d["weather"][0]["description"].title(),
            "rain_chance":      rain_chance,
            "farming_advisory": advisory,
            "status":           "success"
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(404, detail=f"City '{city}' not found")
    except Exception as e:
        raise HTTPException(500, detail=str(e))


"""
=============================================================
MARKET PRICES MODULE
=============================================================
File: backend/routes/market.py
ENDPOINT: GET /api/market/prices
"""
import random
from datetime import datetime

market_router = APIRouter()

# Static crop price database (in production: connect to Agmarknet API)
# Agmarknet API: https://agmarknet.gov.in/
CROP_DATA = [
    {"crop": "Rice",      "category": "cereal",  "market": "Kurnool",     "base": 2100},
    {"crop": "Wheat",     "category": "cereal",  "market": "Guntur",      "base": 2200},
    {"crop": "Maize",     "category": "cereal",  "market": "Nandyal",     "base": 1850},
    {"crop": "Groundnut", "category": "oilseed", "market": "Kurnool",     "base": 5200},
    {"crop": "Soybean",   "category": "oilseed", "market": "Hyderabad",   "base": 4100},
    {"crop": "Toor Dal",  "category": "pulse",   "market": "Hyderabad",   "base": 8500},
    {"crop": "Chana Dal", "category": "pulse",   "market": "Guntur",      "base": 6200},
    {"crop": "Onion",     "category": "vegetable","market": "Kurnool",    "base": 1200},
    {"crop": "Tomato",    "category": "vegetable","market": "Madanapalle","base": 800},
    {"crop": "Chilli",    "category": "spice",   "market": "Guntur",      "base": 9800},
    {"crop": "Cotton",    "category": "fiber",   "market": "Kurnool",     "base": 6200},
    {"crop": "Sugarcane", "category": "cereal",  "market": "Chittoor",    "base": 320},
    {"crop": "Mango",     "category": "fruit",   "market": "Raipur",      "base": 4500},
    {"crop": "Banana",    "category": "fruit",   "market": "Anantapur",   "base": 1800},
]

@market_router.get("/prices")
def get_market_prices(category: str = "all"):
    """
    Return current mandi prices for crops.
    
    In production: Replace with live data from:
    - Agmarknet API (data.gov.in)
    - NCDEX commodity prices
    """
    today = datetime.now().strftime("%d %b %Y %H:%M")

    results = []
    for crop in CROP_DATA:
        if category != "all" and crop["category"] != category:
            continue
        # Simulate daily price fluctuation (±5%)
        variation = random.uniform(-0.05, 0.05)
        price = round(crop["base"] * (1 + variation))
        change = round(variation * 100, 1)

        results.append({
            "crop":     crop["crop"],
            "category": crop["category"],
            "market":   crop["market"],
            "price":    price,
            "unit":     "₹/quintal",
            "change":   change,
            "updated":  today
        })

    return {"data": results, "count": len(results), "status": "success"}


"""
=============================================================
SURVEY MODULE
=============================================================
File: backend/routes/survey.py
ENDPOINT: POST /api/survey/submit
"""
from pydantic import BaseModel as BM
from typing import Optional
import json
from datetime import datetime

survey_router = APIRouter()

class SurveyData(BM):
    name:       str
    village:    str
    crop:       Optional[str] = ""
    challenge:  str
    phone_access: Optional[str] = ""
    language:   Optional[str] = "en"

SURVEY_FILE = "/tmp/survey_responses.json"

@survey_router.post("/submit")
def submit_survey(data: SurveyData):
    """
    Save farmer survey response to file (or database in production).
    
    In production: Save to MySQL/MongoDB database instead of file.
    """
    response = {
        **data.dict(),
        "timestamp": datetime.now().isoformat(),
        "id": f"SUR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

    # Load existing responses
    try:
        with open(SURVEY_FILE, "r") as f:
            responses = json.load(f)
    except: responses = []

    responses.append(response)

    # Save updated list
    with open(SURVEY_FILE, "w") as f:
        json.dump(responses, f, indent=2)

    return {
        "message": "Survey submitted successfully. Thank you!",
        "id": response["id"],
        "status": "success"
    }

@survey_router.get("/stats")
def get_survey_stats():
    """Get aggregated survey statistics for admin dashboard."""
    try:
        with open(SURVEY_FILE, "r") as f:
            responses = json.load(f)
    except: responses = []

    if not responses:
        return {"total": 0, "status": "no data"}

    challenges = {}
    for r in responses:
        c = r.get("challenge", "Unknown")
        challenges[c] = challenges.get(c, 0) + 1

    return {
        "total_responses": len(responses),
        "challenges":      challenges,
        "status":          "success"
    }
