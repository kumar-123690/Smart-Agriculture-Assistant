from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
try:
    import google.generativeai as genai
except Exception as e:
    genai = None
    print(f"Voice AI model not loaded (Google GenAI error): {e}")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    location: str = "Unknown"
    weather: str = "Unknown"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
model = None

if GEMINI_API_KEY and genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Failed to configure Gemini: {e}")
        model = None

@router.post("/")
async def chat_with_bot(req: ChatRequest):
    if not model:
        return {"response": "Hello! I am AgriSmart. To make me fully intelligent, please provide a Gemini API Key in the environment variables."}
    
    prompt = f"""
    You are AgriSmart, an extremely polite, helpful, and expert agricultural AI assistant for farmers.
    The farmer's location is: {req.location}.
    The current weather is: {req.weather}.
    The farmer says: "{req.message}"
    
    Answer the farmer directly, keeping the response short (1-2 sentences), simple, and easy to understand when spoken out loud. Answer in the same language the farmer used.
    """
    try:
        response = model.generate_content(prompt)
        return {"response": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
