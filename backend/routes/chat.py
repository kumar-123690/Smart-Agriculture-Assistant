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

@router.post("")
async def chat_with_bot(req: ChatRequest):
    if not model:
        return {"response": "నమస్తే! నేను అగ్రిస్మార్ట్. మీ వ్యవసాయ సహాయకుడిని. మీకు ఎలా సహాయపడగలను? (Hello! I am AgriSmart. How can I help you?)"}
    
    prompt = f"""
    You are AgriSmart, an expert agricultural AI assistant specifically designed for farmers in India.
    Current Context:
    - Location: {req.location}
    - Weather: {req.weather}
    - Farmer's Query: "{req.message}"
    
    Instructions:
    1. Respond ONLY in Telugu (తెలుగు) unless the farmer explicitly asks for English.
    2. Use very polite and respectful Telugu honorifics (andi, namaste, etc.).
    3. Keep responses short (1-2 sentences).
    4. Provide expert agricultural advice for {req.location}.
    """
    try:
        response = model.generate_content(prompt)
        return {"response": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
