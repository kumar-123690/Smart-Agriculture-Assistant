// ================================================
// UTILITIES
// ================================================
function v(id_) {
  return document.getElementById(id_)?.value || "";
}
function id(id_) {
  return document.getElementById(id_);
}
function show(id_) {
  const el = document.getElementById(id_);
  if (el) el.classList.add("visible");
}

// ================================================
// PARTICLES — Animated background dots
// Creates floating particles dynamically
// ================================================
(function createParticles() {
  const container = document.getElementById("particles");
  if (!container) return;
  for (let i = 0; i < 18; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    const size = Math.random() * 6 + 3;
    p.style.cssText = `
      width:${size}px; height:${size}px;
      left:${Math.random() * 100}%;
      animation-duration:${Math.random() * 15 + 10}s;
      animation-delay:${Math.random() * -20}s;
    `;
    container.appendChild(p);
  }
})();

// ================================================
// SCROLL TO TOP button visibility
// ================================================
window.addEventListener("scroll", () => {
  const btn = document.getElementById("scrollTop");
  if (btn) {
    btn.classList.toggle("visible", window.scrollY > 400);
  }
});

// ================================================
// MOBILE NAV
// ================================================
function openMobileNav() {
  const nav = document.getElementById("mobileNav");
  if (nav) nav.classList.add("open");
}
function closeMobileNav() {
  const nav = document.getElementById("mobileNav");
  if (nav) nav.classList.remove("open");
}

// ================================================
// SCROLL utility
// ================================================
function scrollToSection(id_) {
  document.querySelector(id_)?.scrollIntoView({ behavior: "smooth" });
}

// ================================================
// LANGUAGE TRANSLATIONS DICTIONARY
// ================================================
const translations = {
  en: {
    heroDesc: "AI-powered crop guidance, disease detection, weather forecasting, market prices, and land valuation — all in one platform designed for rural and semi-urban farmers.",
    detect_farm: "Detect My Farm",
    detecting: "Locating...",
    detected: "Detected",
    nav_home: "Home",
    nav_tools: "Tools",
    nav_schemes: "Schemes",
    nav_market: "Market",
    nav_contact: "Contact",
    hero_title: "Empowering Indian Farmers with Smart AI",
    voice_prompt: "మైక్‌ని నొక్కి మీ భాషలో మాట్లాడండి! (Tap the mic and speak!)",
    voice_listen: "Listening...",
    voice_thinking: "Thinking...",
    nav_cta: "Try Now",
    hero_subtitle: "Empowering Indian Farmers with Smart AI",
    hero_title_1: "Smart",
    hero_title_2: "Agriculture",
    hero_title_3: "for Every",
    hero_desc: "AI-powered crop guidance, disease detection, weather forecasting, market prices, and land valuation — all in one platform designed for rural and semi-urban farmers.",
    tool_crop_title: "Crop Recommendation by Soil & Climate",
    tool_disease_title: "Plant Disease Detection by Image",
    tool_market_title: "Market Price Analysis",
    tool_land_title: "Smart Land Valuation",
  },
  te: {
    heroDesc: "AI ఆధారిత పంట మార్గదర్శనం, వ్యాధి గుర్తింపు, వాతావరణ అంచనా, మార్కెట్ ధరలు మరియు భూమి విలువ — అన్ని ఒకే వేదికపై.",
    detect_farm: "నా పొలాన్ని గుర్తించు",
    detecting: "గుర్తిస్తోంది...",
    detected: "గుర్తించబడింది",
    nav_home: "హోమ్",
    nav_tools: "సాధనాలు",
    nav_schemes: "పథకాలు",
    nav_market: "మార్కెట్",
    nav_contact: "సంప్రదించండి",
    hero_title: "స్మార్ట్ AIతో భారతీయ రైతులకు సాధికారత",
    voice_prompt: "మైక్‌ని నొక్కి మాట్లాడండి!",
    voice_listen: "వింటున్నాను...",
    voice_thinking: "ఆలోచిస్తున్నాను...",
    nav_cta: "ప్రయత్నించండి",
    hero_subtitle: "స్మార్ట్ AIతో భారతీయ రైతులకు సాధికారత",
    hero_title_1: "స్మార్ట్",
    hero_title_2: "వ్యవసాయం",
    hero_title_3: "ప్రతి రైతు కోసం",
    hero_desc: "AI-ఆధారిత పంట మార్గదర్శకత్వం, వ్యాధి గుర్తింపు, వాతావరణ సూచన, మార్కెట్ ధరలు మరియు భూమి మూల్యాంకనం — గ్రామీణ రైతులకు రూపొందించబడిన ఒకే వేదిక.",
    tool_crop_title: "నేల మరియు వాతావరణం ద్వారా పంట సిఫార్సు",
    tool_disease_title: "చిత్రం ద్వారా మొక్కల వ్యాధి గుర్తింపు",
    tool_market_title: "మార్కెట్ ధరల విశ్లేషణ",
    tool_land_title: "స్మార్ట్ భూమి మూల్యాంకనం",
  },
};

let currentLang = localStorage.getItem("agri_lang") || "en";

function updateUI() {
  document.querySelectorAll("[data-t]").forEach((el) => {
    const key = el.getAttribute("data-t");
    if (translations[currentLang] && translations[currentLang][key]) {
      el.textContent = translations[currentLang][key];
    }
  });

  // Update language buttons active state
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === currentLang);
  });

  const bubble = id("botBubble");
  if (bubble) {
    bubble.textContent = translations[currentLang].voice_prompt;
  }

  // Update recognition language configuration
  if (recognition) {
    recognition.lang = currentLang === "te" ? "te-IN" : "en-IN";
  }
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("agri_lang", currentLang);
  updateUI();

  const msg =
    currentLang === "te"
      ? "భాష తెలుగులోకి మార్చబడింది."
      : "Language changed to English.";
  speakText(msg, currentLang === "te" ? "te-IN" : "en-US");
}

// ================================================
// CROP RECOMMENDATION — Predict crop
// ================================================
async function predictCrop() {
  const n = +v("crop-n"),
    p = +v("crop-p"),
    k = +v("crop-k"),
    ph = +v("crop-ph"),
    t = +v("crop-temp"),
    h = +v("crop-hum"),
    r = +v("crop-rain");
  if (!n && !p && !ph) {
    alert("Please fill in soil data");
    return;
  }
  const btn = event.target;
  btn.innerHTML = '<span class="spinner"></span>Predicting...';
  btn.disabled = true;
  try {
    const res = await fetch("/api/predict/crop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nitrogen: n,
        phosphorus: p,
        potassium: k,
        ph: ph,
        temperature: t,
        humidity: h,
        rainfall: r,
      }),
    });
    const data = await res.json();
    show("crop-result");
    id("crop-result-val").textContent = data.crop;
    id("crop-result-sub").textContent =
      data.fertilizer_tip + " (Confidence: " + data.confidence + "%)";
  } catch (err) {
    alert("API Error: " + err.message);
  }
  btn.innerHTML = "Predict Best Crop";
  btn.disabled = false;
}

// ================================================
// DISEASE DETECTION — Image upload & predict
// ================================================
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (evt) => {
    id("preview-img").src = evt.target.result;
    id("img-preview").style.display = "block";
  };
  reader.readAsDataURL(file);
}
function handleDrop(e) {
  e.preventDefault();
  id("uploadZone").classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    const dt = new DataTransfer();
    dt.items.add(file);
    id("fileInput").files = dt.files;
    handleFileSelect({ target: id("fileInput") });
  }
}

async function analyzeDisease() {
  const btn = event.target;
  const fileInput = id("fileInput");
  if (!fileInput.files[0]) {
    alert("Please upload an image");
    return;
  }
  btn.innerHTML = '<span class="spinner"></span>Analyzing...';
  btn.disabled = true;
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  try {
    const res = await fetch("/api/predict/disease", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    show("disease-result");
    id("disease-result-val").textContent = data.disease;
    id("disease-result-sub").textContent =
      data.treatment + " (Confidence: " + data.confidence + "%)";
  } catch (err) {
    alert("API Error: " + err.message);
  }
  btn.innerHTML = "Analyze Disease";
  btn.disabled = false;
}

// ================================================
// LAND PRICE PREDICTION
// ================================================
async function predictLandPrice() {
  const state = v("land-state"),
    area = +v("land-area"),
    soil = v("land-soil"),
    irr = v("land-irr"),
    road = +v("land-road");
  if (!state || !area) {
    alert("Fill all land details");
    return;
  }
  const btn = event.target;
  btn.innerHTML = '<span class="spinner"></span>Estimating...';
  btn.disabled = true;
  try {
    const res = await fetch("/api/predict/land", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: state,
        area_acres: area,
        soil_type: +soil,
        irrigation: +irr,
        road_km: road,
      }),
    });
    const data = await res.json();
    show("land-result");
    id("land-result-val").textContent =
      "₹" + data.total_value.toLocaleString("en-IN");
    id("land-result-sub").textContent =
      "≈ ₹" + data.per_acre.toLocaleString("en-IN") + " per acre";
  } catch (err) {
    alert("API Error: " + err.message);
  }
  btn.innerHTML = "Estimate Value";
  btn.disabled = false;
}

// ================================================
// WEATHER — Uses OpenWeatherMap API
// ================================================
async function fetchWeather() {
  const city = v("weather-city").trim();
  if (!city) {
    alert("Enter a city name");
    return;
  }
  const btn =
    typeof event !== "undefined" && event && event.target
      ? event.target
      : document.querySelector('button[onclick="fetchWeather()"]');
  if (btn) btn.innerHTML = "...";
  try {
    const res = await fetch(
      "/api/weather?city=" + encodeURIComponent(city),
    );
    const data = await res.json();
    if (res.status !== 200) {
      alert(data.detail || "City not found");
      if (btn) btn.innerHTML = "Go";
      return;
    }
    id("w-temp").textContent = data.temperature + "°C";
    id("w-desc").textContent = data.description + ` in ${data.city}`;
    id("w-hum").textContent = data.humidity + "%";
    id("w-wind").textContent = data.wind_speed + " km/h";
    id("w-feels").textContent = data.feels_like + "°C";
    id("w-rain").textContent = data.rain_chance + "%";
    const advisory = document.getElementById("w-advisory");
    advisory.style.display = "block";
    advisory.textContent = data.farming_advisory;
  } catch (err) {
    alert("API Error");
  }
  if (btn) btn.innerHTML = "Go";
}

// ================================================
// MARKET PRICES
// ================================================
let currentFilter = "all";
async function renderMarket(filter) {
  const tbody = id("market-tbody");
  if (!tbody) return;
  try {
    const res = await fetch("/api/market/prices?category=" + filter);
    const data = await res.json();
    tbody.innerHTML = data.data
      .map(
        (r) => `
    <tr>
      <td style="font-weight:600">${r.crop}</td>
      <td><span class="badge badge-green" style="font-size:0.7rem;">${r.category}</span></td>
      <td style="color:var(--gray-300)">${r.market}</td>
      <td style="font-weight:700">₹${r.price}</td>
      <td>
        <div class="price-change ${r.change >= 0 ? "price-up" : "price-down"}">
          ${r.change >= 0 ? "▲" : "▼"} ${Math.abs(r.change)}%
        </div>
      </td>
      <td style="color:var(--gray-600);font-size:0.8rem">${r.updated}</td>
    </tr>
  `,
      )
      .join("");
  } catch (err) {
    tbody.innerHTML =
      "<tr><td colspan='6'>Failed to load market data</td></tr>";
  }
}
function filterMarket() {
  currentFilter = v("market-filter");
  renderMarket(currentFilter);
}
function refreshMarket() {
  renderMarket(currentFilter);
}

// ================================================
// SOIL ANALYSIS
// ================================================
function analyzeSoil() {
  const n = +v("soil-n"),
    p = +v("soil-p"),
    k = +v("soil-k"),
    ph = +v("soil-ph"),
    oc = +v("soil-oc"),
    type = v("soil-type");
  if (!n && !ph) {
    alert("Enter soil values");
    return;
  }
  const btn = event.target;
  btn.innerHTML = '<span class="spinner"></span>Analyzing...';
  btn.disabled = true;
  setTimeout(() => {
    const alerts = [];
    if (n < 50)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Low Nitrogen — Apply Urea 120 kg/ha',
      );
    if (n > 150)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> High Nitrogen — Reduce N fertilizer',
      );
    if (p < 25)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Low Phosphorus — Apply DAP 60 kg/ha',
      );
    if (k < 50)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Low Potassium — Apply MOP 80 kg/ha',
      );
    if (ph < 5.5)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Acidic soil — Apply lime 2 t/ha',
      );
    if (ph > 8)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Alkaline soil — Apply gypsum 4 t/ha',
      );
    if (oc < 0.5)
      alerts.push(
        '<i data-lucide="alert-triangle"></i> Low organic matter — Add FYM 5 t/ha',
      );

    show("soil-result");
    id("soil-result-content").innerHTML = alerts.length
      ? `<ul style="list-style:none;display:flex;flex-direction:column;gap:8px;">
         ${alerts.map((a) => `<li style="font-size:0.85rem;color:var(--earth-200)">${a}</li>`).join("")}
       </ul>`
      : `<div style="color:var(--green-400);font-weight:600"><i data-lucide="check-circle"></i> Soil is in good condition for most crops!</div>`;
    
    lucide.createIcons();
    btn.innerHTML = '<i data-lucide="test-tube"></i> Analyze Soil';
    btn.disabled = false;
  }, 1000);
}

// ================================================
// GOVERNMENT SCHEMES DATA
// ================================================
const schemes = [
  {
    icon: '<i data-lucide="banknote"></i>',
    name: "PM-KISAN",
    desc: "₹6,000/year direct income support to eligible farmer families in three equal installments.",
    link: "#",
  },
  {
    icon: '<i data-lucide="wheat"></i>',
    name: "PM Fasal Bima Yojana",
    desc: "Crop insurance scheme providing financial support to farmers suffering crop loss/damage.",
    link: "#",
  },
  {
    icon: '<i data-lucide="droplet"></i>',
    name: "PM Krishi Sinchai Yojana",
    desc: '"Har Khet Ko Pani" — irrigation water to every field through targeted investment for irrigation.',
    link: "#",
  },
  {
    icon: '<i data-lucide="test-tube"></i>',
    name: "Soil Health Card",
    desc: "Free soil testing and Health Card to farmers with crop-wise recommendations for nutrients.",
    link: "#",
  },
  {
    icon: '<i data-lucide="smartphone"></i>',
    name: "e-NAM",
    desc: "National Agriculture Market — online trading platform connecting farmers to multiple buyers.",
    link: "#",
  },
  {
    icon: '<i data-lucide="leaf"></i>',
    name: "Paramparagat Krishi",
    desc: "Cluster-based organic farming with financial assistance, capacity building, and market support.",
    link: "#",
  },
];

function loadSchemes() {
  const grid = document.getElementById("schemes-grid");
  if (!grid) return;
  grid.innerHTML = schemes
    .map(
      (s) => `
    <div class="scheme-card">
      <div class="spotlight"></div>
      <div class="scheme-icon">${s.icon}</div>
      <div class="scheme-name">${s.name}</div>
      <p class="scheme-desc">${s.desc}</p>
      <a href="${s.link}" class="scheme-link">Learn More →</a>
    </div>
  `,
    )
    .join("");
}

// ================================================
// SURVEY FORM SUBMISSION
// ================================================
async function submitSurvey() {
  const name = v("s-name"),
    village = v("s-village"),
    challenge = v("s-challenge"),
    crop = v("s-crop"),
    phone = v("s-phone");
  if (!name || !village || !challenge) {
    alert("Please fill all required fields");
    return;
  }
  const btn = event.target;
  btn.innerHTML = '<span class="spinner"></span>Submitting...';
  btn.disabled = true;
  try {
    const res = await fetch("/api/survey/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        village: village,
        challenge: challenge,
        crop: crop,
        phone_access: phone,
      }),
    });
    if (res.ok) {
      id("survey-success").style.display = "block";
      btn.style.display = "none";
      ["s-name", "s-village", "s-crop", "s-challenge", "s-phone"].forEach(
        (f) => {
          const el = id(f);
          if (el.tagName === "SELECT") el.selectedIndex = 0;
          else el.value = "";
        },
      );
    }
  } catch (err) {
    alert("Failed to submit");
    btn.innerHTML = "Submit Feedback →";
    btn.disabled = false;
  }
}

// ================================================
// INTERSECTION OBSERVER — Animate cards on scroll
// ================================================
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        e.target.style.animationDelay = i * 0.1 + "s";
        e.target.classList.add("fade-in");
        observer.unobserve(e.target);
      }
    });
  },
  { threshold: 0.1 },
);

function initScrollAnimations() {
  document
    .querySelectorAll(".feature-card, .scheme-card, .tech-card, .step")
    .forEach((el) => {
      observer.observe(el);
    });
}

// ================================================
// GEOLOCATION (GPS Reverse Geocoding)
// ================================================
let userLocation = "Unknown";
let userWeather = "Unknown";

async function detectLocation() {
  try {
    console.log("Starting auto-location detection...");
    const btn = id("gpsBtn");
    if (!btn) {
      console.error("GPS Button not found!");
      return;
    }

    if (btn.dataset.loading === "true") return;
    btn.dataset.loading = "true";

    btn.innerHTML = `<span class="spinner"></span> <span data-t="detecting">${translations[currentLang].detecting}</span>`;

    const setIdle = () => {
      btn.dataset.loading = "false";
      btn.innerHTML = `<i data-lucide="map-pin"></i> <span data-t="detect_farm">${translations[currentLang].detect_farm}</span>`;
      lucide.createIcons();
    };

    const handleSuccess = async (city, state) => {
      console.log("Location Success:", city, state);
      userLocation = `${city}, ${state}`;

      localStorage.setItem(
        "agri_location",
        JSON.stringify({ city, state }),
      );

      btn.innerHTML = `<i data-lucide="check"></i> <span data-t="detected">${translations[currentLang].detected}</span>`;
      lucide.createIcons();

      const locDisp = id("locationDisplay");
      if (locDisp) {
        locDisp.style.display = "flex";
        locDisp.style.alignItems = "center";
        locDisp.style.gap = "6px";
        locDisp.innerHTML = `
          <i data-lucide="map-pin" style="width:14px;height:14px;"></i> ${userLocation}
        `;
        lucide.createIcons();
      }

      const cityInput = id("weather-city");
      if (cityInput) {
        cityInput.value = city;
        await fetchWeather();
      }

      speakText(
        `Location detected as ${city}. I am AgriSmart. How can I help you today?`,
        currentLang === "te" ? "te-IN" : "en-IN"
      );

      btn.dataset.loading = "false";
    };

    const fetchWithTimeout = (url, timeout = 8000) => {
      return Promise.race([
        fetch(url),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error("Request timeout")), timeout),
        ),
      ]);
    };

    const fallbackToIP = async () => {
      console.log("Falling back to IP location...");
      try {
        const res = await fetchWithTimeout("https://ipapi.co/json/");
        const data = await res.json();

        if (data.city) {
          await handleSuccess(data.city, data.region);
        } else {
          throw new Error("No city from IP");
        }
      } catch (e) {
        console.error("IP Location Error:", e);
        setIdle();
        speakText(
          "Unable to detect location. Please enter your city manually.",
          currentLang === "te" ? "te-IN" : "en-US"
        );
      }
    };

    const cached = localStorage.getItem("agri_location");
    if (cached) {
      try {
        const { city, state } = JSON.parse(cached);
        if (city && state) {
          console.log("Using cached location:", city);
          await handleSuccess(city, state);
          return;
        }
      } catch (e) {
        console.error("Cache Error:", e);
      }
    }

    if (!navigator.geolocation) {
      console.log("Geolocation not supported.");
      await fallbackToIP();
      return;
    }

    console.log("Requesting GPS coordinates...");
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude: lat, longitude: lon } = pos.coords;
        try {
          const res = await fetchWithTimeout(
            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&accept-language=en`,
          );
          const data = await res.json();
          const addr = data.address || {};
          const city =
            addr.village ||
            addr.town ||
            addr.city ||
            addr.suburb ||
            addr.county ||
            "Your Area";
          const state = addr.state || "";
          await handleSuccess(city, state);
        } catch (e) {
          console.error("Geocode Error:", e);
          await fallbackToIP();
        }
      },
      async (err) => {
        console.warn("GPS Error:", err.message);
        await fallbackToIP();
      },
      { timeout: 10000, enableHighAccuracy: true },
    );
  } catch (globalErr) {
    console.error("Fatal DetectLocation Error:", globalErr);
  }
}

// ================================================
// VOICE ASSISTANT (Speech Recognition + TTS)
// ================================================
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isListening = false;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = currentLang === "te" ? "te-IN" : "en-IN";
  recognition.interimResults = false;

  recognition.onstart = function () {
    isListening = true;
    id("voiceBtn").classList.add("listening");
    id("botBubble").style.display = "block";
    id("botBubble").textContent = translations[currentLang].voice_listen || "Listening...";
  };

  recognition.onresult = async function (event) {
    const transcript = event.results[0][0].transcript;
    id("botBubble").textContent = `You: "${transcript}"`;
    await sendToChatbot(transcript);
  };

  recognition.onerror = function (event) {
    id("botBubble").textContent = "Didn't catch that. Tap to try again.";
    stopListening();
  };

  recognition.onend = function () {
    stopListening();
  };
}

function toggleVoice() {
  if (!SpeechRecognition) {
    alert("Your browser doesn't support Voice AI. Try Chrome or Edge.");
    return;
  }
  if (isListening) {
    recognition.stop();
  } else {
    window.speechSynthesis.cancel();
    recognition.start();
  }
}

function stopListening() {
  isListening = false;
  const voiceBtn = id("voiceBtn");
  if (voiceBtn) voiceBtn.classList.remove("listening");
}

async function sendToChatbot(text) {
  id("botBubble").textContent = translations[currentLang].voice_thinking || "Thinking...";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        location: userLocation,
        weather: document.getElementById("w-desc")?.textContent || "Unknown",
      }),
    });
    const data = await res.json();
    id("botBubble").textContent = data.response;
    speakText(data.response, currentLang === "te" ? "te-IN" : "en-IN");
  } catch (err) {
    id("botBubble").textContent = "Sorry, I am having trouble connecting.";
  }
}

function speakText(text, lang = "te-IN") {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  window.speechSynthesis.speak(utterance);
}

// ================================================
// SPOTLIGHT CARD EFFECT
// ================================================
function initSpotlightEffect() {
  document.querySelectorAll(".feature-card, .tool-card, .scheme-card, .tech-card").forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty("--x", x + "px");
      card.style.setProperty("--y", y + "px");
    });
  });
}

// ================================================
// INITIALIZATION
// ================================================
window.addEventListener("load", () => {
  try {
    // Update select element attributes on change to fix floating label overlap
    document.querySelectorAll(".form-select").forEach((select) => {
      select.setAttribute("value", select.value);
      select.addEventListener("change", () => {
        select.setAttribute("value", select.value);
      });
    });

    loadSchemes();
    updateUI();
    initScrollAnimations();
    initSpotlightEffect();
    lucide.createIcons();
    console.log("App initialized, triggering auto-location...");
    setTimeout(detectLocation, 1000);
  } catch (e) {
    console.error("Initialization Error:", e);
  }
});
