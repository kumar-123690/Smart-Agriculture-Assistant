# 🌿 Smart Agriculture Assistant (AgriSmart)

### AI-Powered Farmer Support System | CSP Project — CSE Department

> **Submitted by:** M Prem Kumar, P Gowthami, T Mrudula
> **Guided by:** M Tharun Kumar Sir  
> **Department:** Computer Science & Engineering  

---

## 📌 Project Overview

**AgriSmart** is a unified, full-stack, AI-powered agricultural helper system specifically designed to empower rural and semi-urban Indian farmers. By combining advanced Machine Learning, Computer Vision, and Generative AI, the platform provides critical tools to optimize crop yield, detect diseases, estimate land value, and get real-time voice-guided agricultural advisories in regional languages.

### 🌟 Key Features
- 🌾 **Crop Recommendation:** Suggests the most suitable crop using real-time soil (N, P, K, pH) and climate (temperature, humidity, rainfall) inputs, powered by a **Random Forest Classifier (~99.3% accuracy)**.
- 🔬 **Leaf Disease Detection:** Automatically identifies crop diseases from leaf photos and provides immediate organic and chemical treatment advice. Powered by a **CNN / MobileNetV2 Transfer Learning Model (~96.5% accuracy)**.
- 🏡 **Smart Land Valuation:** Estimates total and per-acre land value based on regional parameters (state, area, soil type, irrigation availability, and road proximity) using a **Gradient Boosting Regressor (R² ~0.91)**.
- ⛅ **Live Weather & Farming Advisory:** Fetches real-time weather information using the OpenWeatherMap API and displays tailored, actionable agricultural guidance based on local heat, humidity, or rainfall likelihood.
- 📊 **Mandi Market Price Tracker:** Displays real-time commodity prices (mandi rates) for over 50+ crops across major hubs, complete with trend indicators (up/down percentage changes).
- 🧪 **Soil Health Analysis:** Interactively analyzes soil nutrient profiles (N, P, K, pH, Organic Carbon) to recommend exact fertilizer dosages (e.g., Urea, DAP, MOP, Gypsum, or lime treatment).
- 🌐 **Seamless Multilingual Support:** High-quality localization for both **English** and **Telugu (తెలుగు)**, persisting language selections using browser local storage.
- 📍 **Auto-Location Detection ("Detect My Farm"):** Integrates geolocation to auto-detect the farm's location. Uses OpenStreetMap Nominatim reverse-geocoding, with a fail-safe IP geolocation fallback (`ipapi.co`) for local hosting environments.
- 🎙️ **Multilingual Voice AI Chatbot:** An interactive voice-enabled chatbot powered by **Google Gemini 1.5 Flash**. Farmers can talk to the bot (speech-to-text) and receive spoken responses (text-to-speech) with expert farming advice customized for their detected location and weather conditions.

---

## 🗂️ Project Structure

```
smart-agri/
│
├── frontend/
│   ├── index.html          ← Complete responsive web interface (HTML + Glassmorphism CSS)
│   └── assets/
│       └── app.js          ← Main frontend logic (CORS API calls, Geolocation, Speech APIs, Translation)
│
├── backend/
│   ├── main.py             ← FastAPI entry point & unified frontend file server
│   ├── requirements.txt    ← Python package dependencies
│   │
│   ├── routes/
│   │   ├── crop.py         ← POST /api/predict/crop
│   │   ├── disease.py      ← POST /api/predict/disease
│   │   ├── land.py         ← POST /api/predict/land
│   │   ├── weather.py      ← GET  /api/weather
│   │   ├── market.py       ← GET  /api/market/prices
│   │   ├── survey.py       ← POST /api/survey/submit
│   │   └── chat.py         ← POST /api/chat (Gemini AI voice companion)
│   │
│   └── ml_models/
│       ├── train_models.py ← Training pipeline script for Crop and Land ML models
│       ├── crop_model.pkl  ← Trained Random Forest model + encoder payload
│       ├── land_model.pkl  ← Trained Gradient Boosting regressor model
│       └── disease_model.h5← Pre-trained leaf disease classification model (CNN/MobileNetV2)
│
├── run_server.py           ← Main script to start backend & serve frontend automatically
├── Dockerfile              ← Multistage slim build configuration
├── docker-compose.yml      ← Local environment container orchestration
└── README.md
```

---

## 🔌 API Endpoints Reference

All endpoints are fully documented in the FastAPI Swagger UI at `http://localhost:8000/docs`.

| Method | Endpoint              | Purpose                           | Key Inputs / Parameters                     |
|:-------|:----------------------|:----------------------------------|:--------------------------------------------|
| `POST` | `/api/predict/crop`   | Recommend optimal crop            | N, P, K, pH, temp, humidity, rainfall       |
| `POST` | `/api/predict/disease`| Detect plant leaf disease         | Leaf image file (Multipart form upload)     |
| `POST` | `/api/predict/land`   | Land price valuation estimation   | State code, area, soil type, irrigation, road|
| `GET`  | `/api/weather`        | Fetch real-time weather & advisory| `city` query parameter (e.g. `Kurnool`)      |
| `GET`  | `/api/market/prices`  | Crop Mandi price index tracking   | `category` filter parameter (`all`/`grain` etc) |
| `POST` | `/api/survey/submit`  | Submit farmer challenge surveys   | Name, village, crop, challenge statement    |
| `POST` | `/api/chat`           | Chatbot conversation engine       | Message, detected location, weather context  |

---

## 🚀 Installation & Local Setup

### Prerequisites
- **Python 3.8+** installed.
- Internet connection (for Nominatim geocoding, Google Gemini, and OpenWeatherMap APIs).

### Step 1: Clone the Repository
```bash
git clone https://github.com/middepremkumar/Smart-Agriculture-Assistant.git
cd Smart-Agriculture-Assistant
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Train Machine Learning Models
Generate the predictive models (`crop_model.pkl` and `land_model.pkl`) using the integrated training pipeline script:
```bash
python backend/ml_models/train_models.py
```
> **Note:** The Disease Detection model (`disease_model.h5`) can be trained on Google Colab using the training guide outlined in `train_models.py` and placed in the `backend/ml_models/` folder.

### Step 4: Configure API Credentials
Create a `.env` file in the root directory (or in the `backend/` directory) to configure external service keys:
```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```
- **Weather Key:** Register for a free API key at [OpenWeatherMap](https://openweathermap.org/api).
- **Gemini Key:** Generate a free API key at [Google AI Studio](https://aistudio.google.com/).

### Step 5: Start the Server
Run the unified server entry script:
```bash
python run_server.py
```
The server will boot up using Uvicorn and bind to:
- **Application URL:** [http://localhost:8000](http://localhost:8000) (Serves the interactive frontend web app)
- **API Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) (For exploring and testing API endpoints)

---

## 🐳 Running with Docker

Alternatively, you can run the entire system inside a Docker container without needing to set up Python locally.

### Using Docker Compose
1. Open `docker-compose.yml` and add your API keys or define them in your environment.
2. Build and run:
   ```bash
   docker-compose up --build
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🤖 Machine Learning Model Architecture

### 1. Crop Recommendation
- **Algorithm:** Random Forest Classifier (200 ensemble decision trees)
- **Input:** 7 agricultural variables (N, P, K, pH, temperature, humidity, rainfall)
- **Output:** Best crop suggestion + confidence percentage + fertilizer treatment recommendation
- **Dataset:** Standard Crop Recommendation Dataset (2,200 rows covering 22 diverse crops)
- **R² / Accuracy:** ~99.3%

### 2. Leaf Disease Detection
- **Architecture:** CNN / MobileNetV2 (Utilizes transfer learning with frozen pre-trained ImageNet weights)
- **Input:** 224x224 RGB image of the affected plant leaf
- **Output:** Predicted disease class name + confidence percentage + treatment advisory
- **Dataset:** PlantVillage Dataset (54,309 images encompassing 38 unique healthy & diseased classes)
- **Validation Accuracy:** ~96.5%

### 3. Smart Land Price Regressor
- **Algorithm:** Gradient Boosting Regressor (200 estimator trees, depth = 5)
- **Input:** State code, area in acres, soil type, irrigation tier, and road proximity in km
- **Output:** Projected total valuation (INR) + calculated per-acre valuation (INR)
- **R² Score:** ~0.91

---

## 🌾 Team & Guideline Credits

| Role | Responsibilities |
|------|-----------------|
| **Frontend Dev** | HTML, Responsive glassmorphic layout, local storage localization, speech synthesis/recognition API integrations |
| **Backend Dev** | FastAPI app core, CORS middleware, API endpoint routers, static assets folder serving |
| **ML Engineer** | Model training scripts (`train_models.py`), Random Forest/Gradient Boosting optimization, Google Colab transfer learning config |
| **DB & Testing** | Mock Mandi data creation, API manual and automated tests, bug troubleshooting, schema design |

---

*Built with passion to support Indian farmers using technology 🌾*
