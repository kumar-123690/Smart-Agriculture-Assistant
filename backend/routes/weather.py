from fastapi import APIRouter
from fastapi import Query
import httpx
import os

router = APIRouter()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

@router.get("")
async def get_weather(city: str = Query(..., description="City name")):
    """
    Fetch real-time weather from OpenWeatherMap API.
    
    HOW TO GET API KEY:
    1. Sign up free at https://openweathermap.org/api
    2. Copy your API key
    3. Set env variable: export OPENWEATHER_API_KEY=your_key
    4. Or set it in .env file: OPENWEATHER_API_KEY=your_key
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY == "your_api_key_here":
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
