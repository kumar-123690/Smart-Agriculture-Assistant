"""
=============================================================
SMART AGRICULTURE ASSISTANT — FastAPI Backend
=============================================================
File: backend/main.py

This is the main entry point of the backend server.
It registers all route modules and starts the CORS-enabled API.

HOW IT WORKS:
- FastAPI creates a REST API server on port 8000
- Each feature (crop, disease, land, weather) is a separate router
- ML models are loaded once at startup (not on every request)
- CORS allows the frontend (React/HTML) to call this API
=============================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import route modules
from routes.crop import router as crop_router
from routes.disease import router as disease_router
from routes.land import router as land_router
from routes.weather import router as weather_router
from routes.survey import router as survey_router
from routes.market import router as market_router

# ===== CREATE APP =====
app = FastAPI(
    title="Smart Agriculture Assistant API",
    description="AI-powered agriculture assistance for Indian farmers",
    version="1.0.0"
)

# ===== CORS SETTINGS =====
# Allows the React frontend to call this backend
# In production, replace "*" with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Change to ["https://yourdomain.com"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== REGISTER ROUTES =====
# Each router handles one feature module
app.include_router(crop_router,    prefix="/api/predict",  tags=["Crop Recommendation"])
app.include_router(disease_router, prefix="/api/predict",  tags=["Disease Detection"])
app.include_router(land_router,    prefix="/api/predict",  tags=["Land Price"])
app.include_router(weather_router, prefix="/api/weather",  tags=["Weather"])
app.include_router(survey_router,  prefix="/api/survey",   tags=["Survey"])
app.include_router(market_router,  prefix="/api/market",   tags=["Market Prices"])

# ===== HEALTH CHECK ENDPOINT =====
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Smart Agriculture Assistant API",
        "docs": "/docs"  # Auto-generated Swagger UI
    }

# ===== RUN SERVER =====
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # reload=True means server restarts on code change (use only in development)
