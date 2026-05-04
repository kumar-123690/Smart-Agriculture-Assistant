import os
import re
import shutil

def main():
    # 1. Update Requirements
    req_file = "requirements.txt"
    with open(req_file, "r") as f:
        reqs = f.read()
    if "google-generativeai" not in reqs:
        with open(req_file, "a") as f:
            f.write("\ngoogle-generativeai==0.3.1\n")

    # 2. Fix Directory Structure
    os.makedirs("routes", exist_ok=True)
    open("routes/__init__.py", "w").close()
    
    # Move crop and disease to routes if they exist in root
    for file in ["crop.py", "disease.py"]:
        if os.path.exists(file):
            shutil.move(file, os.path.join("routes", file))
            
    # Split all_routes.py if it exists
    if os.path.exists("all_routes.py"):
        with open("all_routes.py", "r", encoding="utf-8") as f:
            all_r = f.read()
            
        land = re.search(r'"""\n===+.*?LAND PRICE PREDICTION.*?ENDPOINT: POST /api/predict/land\n"""(.*?)"""\n===+', all_r, re.DOTALL)
        if land:
            with open("routes/land.py", "w", encoding="utf-8") as f: f.write(land.group(1).strip() + "\n")
            
        weather = re.search(r'WEATHER MODULE\n===+.*?\n"""(.*?)(?:"""\n===+|$)', all_r, re.DOTALL)
        if weather:
            with open("routes/weather.py", "w", encoding="utf-8") as f: f.write("from fastapi import APIRouter\n" + weather.group(1).strip() + "\n")
            
        market = re.search(r'MARKET PRICES MODULE\n===+.*?\n"""(.*?)(?:"""\n===+|$)', all_r, re.DOTALL)
        if market:
            with open("routes/market.py", "w", encoding="utf-8") as f: f.write("from fastapi import APIRouter\n" + market.group(1).strip() + "\n")
            
        survey = re.search(r'SURVEY MODULE\n===+.*?\n"""(.*?)(?:"""\n===+|$)', all_r, re.DOTALL)
        if survey:
            with open("routes/survey.py", "w", encoding="utf-8") as f: f.write("from fastapi import APIRouter\n" + survey.group(1).strip() + "\n")

    # 3. Create chat.py
    chat_code = '''from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import google.generativeai as genai

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    location: str = "Unknown"
    weather: str = "Unknown"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
model = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

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
'''
    with open("routes/chat.py", "w", encoding="utf-8") as f:
        f.write(chat_code)

    # 4. Update main.py
    with open("main.py", "r", encoding="utf-8") as f:
        main_code = f.read()
    if "from routes.chat import router as chat_router" not in main_code:
        main_code = main_code.replace("from routes.market import router as market_router", "from routes.market import router as market_router\nfrom routes.chat import router as chat_router")
        main_code = main_code.replace("app.include_router(market_router,  prefix=\"/api/market\",   tags=[\"Market Prices\"])", "app.include_router(market_router,  prefix=\"/api/market\",   tags=[\"Market Prices\"])\napp.include_router(chat_router,    prefix=\"/api/chat\",     tags=[\"Voice AI Chatbot\"])")
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(main_code)

    # 5. Update index.html
    html_file = "index.html"
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    css_inject = '''
    /* =============================================
       VOICE AI & GPS
    ============================================= */
    .gps-btn {
      position: fixed;
      top: 100px; right: 24px;
      z-index: 100;
      padding: 10px 16px;
      background: rgba(10,46,26,0.85);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(46,204,113,0.3);
      border-radius: 99px;
      color: var(--green-400);
      font-weight: 600;
      display: flex; align-items: center; gap: 8px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      cursor: pointer; transition: 0.3s;
    }
    .gps-btn:hover { background: var(--green-600); color: var(--white); }
    
    .voice-bot {
      position: fixed;
      bottom: 24px; left: 24px;
      z-index: 200;
      display: flex; flex-direction: column; gap: 12px; align-items: flex-start;
    }
    .bot-bubble {
      background: rgba(15,69,38,0.9);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(46,204,113,0.4);
      padding: 14px 18px;
      border-radius: 20px 20px 20px 0;
      color: var(--white);
      max-width: 280px;
      font-size: 0.9rem;
      line-height: 1.5;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      display: none;
      animation: fadeIn 0.3s ease;
    }
    .bot-btn {
      width: 64px; height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--green-600), var(--green-800));
      border: 2px solid var(--green-400);
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 8px 24px rgba(46,204,113,0.3);
      cursor: pointer; transition: 0.3s;
      position: relative;
    }
    .bot-btn:hover { transform: scale(1.05); }
    .bot-btn.listening {
      animation: pulse-ring 1.5s infinite;
      background: var(--red-400); border-color: var(--white);
    }
    .bot-btn.listening .lucide { color: var(--white); }
    @keyframes pulse-ring {
      0% { box-shadow: 0 0 0 0 rgba(239,83,80,0.6); }
      70% { box-shadow: 0 0 0 20px rgba(239,83,80,0); }
      100% { box-shadow: 0 0 0 0 rgba(239,83,80,0); }
    }
    '''
    if "VOICE AI & GPS" not in html:
        html = html.replace("</style>", css_inject + "\n  </style>")

    ui_inject = '''
  <!-- Detect Location -->
  <button class="gps-btn" onclick="detectLocation()" id="gpsBtn">
    <i data-lucide="map-pin"></i> <span>Detect My Farm</span>
  </button>

  <!-- Voice Assistant -->
  <div class="voice-bot">
    <div class="bot-bubble" id="botBubble">Tap the mic and speak in your language!</div>
    <button class="bot-btn" onclick="toggleVoice()" id="voiceBtn">
      <i data-lucide="mic" style="width:28px;height:28px;color:white;"></i>
    </button>
  </div>
    '''
    if "<!-- Voice Assistant -->" not in html:
        html = html.replace("</body>", ui_inject + "\n</body>")

    js_inject = '''
    // ================================================
    // GEOLOCATION & AUTOMATION
    // ================================================
    let userLocation = "Unknown";
    let userWeather = "Unknown";

    async function detectLocation() {
      const btn = id('gpsBtn');
      btn.innerHTML = '<span class="spinner"></span> Locating...';
      if (!navigator.geolocation) {
        alert("Geolocation not supported by your browser");
        btn.innerHTML = '<i data-lucide="map-pin"></i> <span>Detect My Farm</span>';
        lucide.createIcons();
        return;
      }
      navigator.geolocation.getCurrentPosition(async pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        try {
          // Reverse geocode via Nominatim
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
          const data = await res.json();
          const city = data.address.city || data.address.town || data.address.village || data.address.county || "Your Area";
          const state = data.address.state || "";
          userLocation = `${city}, ${state}`;
          
          btn.innerHTML = `<i data-lucide="check"></i> <span>${city}</span>`;
          lucide.createIcons();
          
          // Auto trigger weather
          const cityInput = id('weather-city');
          if(cityInput) {
            cityInput.value = city;
            await fetchWeather(); // Will update userWeather internally
          }
          
          // Say hello
          speakText(`Location detected as ${city}. I am AgriSmart. How can I help you today?`);
        } catch(e) {
          btn.innerHTML = '<i data-lucide="map-pin"></i> <span>Detect My Farm</span>';
          lucide.createIcons();
        }
      }, err => {
        alert("Could not get location. Please allow GPS permissions.");
        btn.innerHTML = '<i data-lucide="map-pin"></i> <span>Detect My Farm</span>';
        lucide.createIcons();
      });
    }

    // ================================================
    // VOICE ASSISTANT (Speech Recognition + TTS)
    // ================================================
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let isListening = false;

    if (SpeechRecognition) {
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      // Allow any language, browser tries to auto-detect or use OS default
      recognition.lang = navigator.language || 'en-IN'; 
      recognition.interimResults = false;

      recognition.onstart = function() {
        isListening = true;
        id('voiceBtn').classList.add('listening');
        id('botBubble').style.display = 'block';
        id('botBubble').textContent = "Listening...";
      };

      recognition.onresult = async function(event) {
        const transcript = event.results[0][0].transcript;
        id('botBubble').textContent = `You: "${transcript}"`;
        await sendToChatbot(transcript);
      };

      recognition.onerror = function(event) {
        id('botBubble').textContent = "Didn't catch that. Tap to try again.";
        stopListening();
      };

      recognition.onend = function() {
        stopListening();
      };
    }

    function toggleVoice() {
      if (!SpeechRecognition) {
        alert("Your browser doesn't support Voice AI. Try Chrome or Edge.");
        return;
      }
      if (isListening) recognition.stop();
      else {
        window.speechSynthesis.cancel(); // stop current speaking
        recognition.start();
      }
    }

    function stopListening() {
      isListening = false;
      id('voiceBtn').classList.remove('listening');
    }

    async function sendToChatbot(text) {
      id('botBubble').textContent = "Thinking...";
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            location: userLocation,
            weather: document.getElementById('w-desc')?.textContent || "Unknown"
          })
        });
        const data = await res.json();
        id('botBubble').textContent = data.response;
        speakText(data.response);
      } catch(err) {
        id('botBubble').textContent = "Sorry, I am having trouble connecting.";
      }
    }

    function speakText(text) {
      if (!window.speechSynthesis) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      // Auto detect language roughly based on text content, or rely on OS default
      window.speechSynthesis.speak(utterance);
    }
    '''
    if "GEOLOCATION & AUTOMATION" not in html:
        html = html.replace("lucide.createIcons();", "lucide.createIcons();\n" + js_inject)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print("Voice & Geolocation Integrated Successfully")

if __name__ == "__main__":
    main()
