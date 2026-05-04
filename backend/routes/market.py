from fastapi import APIRouter
import random
from datetime import datetime

router = APIRouter()

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

@router.get("/prices")
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
        # Simulate daily price fluctuation (Â±5%)
        variation = random.uniform(-0.05, 0.05)
        price = round(crop["base"] * (1 + variation))
        change = round(variation * 100, 1)

        results.append({
            "crop":     crop["crop"],
            "category": crop["category"],
            "market":   crop["market"],
            "price":    price,
            "unit":     "â‚¹/quintal",
            "change":   change,
            "updated":  today
        })

    return {"data": results, "count": len(results), "status": "success"}
