from fastapi import APIRouter
from pydantic import BaseModel as BM
from typing import Optional
import json
from datetime import datetime

router = APIRouter()

class SurveyData(BM):
    name:       str
    village:    str
    crop:       Optional[str] = ""
    challenge:  str
    phone_access: Optional[str] = ""
    language:   Optional[str] = "en"

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
SURVEY_FILE = os.path.join(DATA_DIR, "survey_responses.json")

@router.post("/submit")
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

@router.get("/stats")
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
