import re
import os

def update_html():
    filepath = r"c:\cspproject\index.html"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS FIXES (Alignment and Floating labels)
    css_fixes = """
    /* Form Floating Labels Fixes */
    .form-group {
      position: relative;
      margin-bottom: 24px;
      display: flex;
      flex-direction: column-reverse;
    }
    .form-input, .form-select {
      width: 100%;
      padding: 20px 16px 8px;
      background: rgba(10,46,26,0.6);
      border: 1px solid rgba(46,204,113,0.2);
      border-radius: var(--radius-sm);
      color: var(--white);
      font-size: 0.95rem;
      transition: all 0.2s ease;
    }
    .form-label {
      position: absolute;
      top: 16px;
      left: 16px;
      font-size: 0.95rem;
      color: var(--gray-600);
      pointer-events: none;
      transition: all 0.2s ease;
    }
    .form-input:focus ~ .form-label,
    .form-input:not(:placeholder-shown) ~ .form-label,
    .form-select:focus ~ .form-label,
    .form-select:not([value=""]) ~ .form-label {
      top: 6px;
      font-size: 0.7rem;
      color: var(--green-400);
      font-weight: 600;
    }
    
    /* Icon alignment fixes */
    .btn-primary, .btn-outline {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      justify-content: center;
    }
    .feature-icon, .scheme-icon, .upload-icon {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    """
    if "flex-direction: column-reverse;" not in content:
        content = content.replace("/* Form Floating Labels */", css_fixes + "\n/* Old Form Floating Labels */")

    # 2. REMOVE NON-FARMER CONTENT
    # Remove Hero Tag "Community Service Project"
    content = re.sub(r'<div class="hero-tag">.*?Community Service Project.*?</div>', '', content, flags=re.DOTALL)
    
    # Remove Tech Stack Section
    content = re.sub(r'<!-- ===== TECH STACK ===== -->.*?<!-- ===== SURVEY / FEEDBACK ===== -->', '<!-- ===== SURVEY / FEEDBACK ===== -->', content, flags=re.DOTALL)
    
    # Clean Survey Section Text
    content = content.replace("As part of our Community Service Project, we are conducting a survey", "We are conducting a survey")
    content = content.replace("Help Us Serve<br/>You Better", "Farmer<br/>Feedback")
    
    # Clean Footer Text
    content = content.replace("A Community Service Project by Department of Computer Science & Engineering, empowering farmers with AI-driven insights.", "Empowering farmers with AI-driven insights and real-time market data.")
    content = re.sub(r'<p style="margin-top:12px;font-size:0.8rem;color:var(--gray-600);">Submitted by: P Gowthami<br/>Guided by: M Tharun Kumar Sir</p>', '', content, flags=re.DOTALL)
    content = content.replace("© 2025 AgriSmart — CSP Project, CSE Dept", "© 2025 AgriSmart")
    
    # Remove tech stack from footer links
    content = re.sub(r'<div class="footer-col">\s*<h5>Tech Stack</h5>.*?</div>', '', content, flags=re.DOTALL)
    
    # Remove Tech Stack nav link
    content = re.sub(r'<li><a href="#tech">Tech Stack</a></li>', '', content)
    content = re.sub(r'<a href="#tech" onclick="closeMobileNav\(\)">Tech Stack</a>', '', content)

    # 3. BACKEND API INTEGRATIONS
    # Replace JS functions with real fetch calls
    
    # Crop API
    crop_js = """
    async function predictCrop() {
      const n=+v('crop-n'), p=+v('crop-p'), k=+v('crop-k'),
            ph=+v('crop-ph'), t=+v('crop-temp'), h=+v('crop-hum'), r=+v('crop-rain');
      if (!n && !p && !ph) { alert('Please fill in soil data'); return; }
      const btn = event.target;
      btn.innerHTML = '<span class="spinner"></span>Predicting...';
      btn.disabled = true;
      try {
        const res = await fetch('/api/predict/crop', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nitrogen: n, phosphorus: p, potassium: k, ph: ph, temperature: t, humidity: h, rainfall: r })
        });
        const data = await res.json();
        show('crop-result');
        id('crop-result-val').textContent = data.crop;
        id('crop-result-sub').textContent = data.fertilizer_tip + " (Confidence: " + data.confidence + "%)";
      } catch (err) {
        alert("API Error: " + err.message);
      }
      btn.innerHTML = 'Predict Best Crop';
      btn.disabled = false;
    }
    """
    content = re.sub(r'function predictCrop\(\) \{.*?\n    \}', crop_js, content, flags=re.DOTALL)

    # Disease API
    disease_js = """
    async function analyzeDisease() {
      const btn = event.target;
      const fileInput = id('fileInput');
      if (!fileInput.files[0]) { alert('Please upload an image'); return; }
      btn.innerHTML = '<span class="spinner"></span>Analyzing...';
      btn.disabled = true;
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      try {
        const res = await fetch('/api/predict/disease', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        show('disease-result');
        id('disease-result-val').textContent = data.disease;
        id('disease-result-sub').textContent = data.treatment + " (Confidence: " + data.confidence + "%)";
      } catch (err) {
        alert("API Error: " + err.message);
      }
      btn.innerHTML = 'Analyze Disease';
      btn.disabled = false;
    }
    """
    content = re.sub(r'function analyzeDisease\(\) \{.*?\n    \}', disease_js, content, flags=re.DOTALL)

    # Land API
    land_js = """
    async function predictLandPrice() {
      const state = v('land-state'), area = +v('land-area'),
            soil = v('land-soil'), irr = v('land-irr'), road = +v('land-road');
      if (!state || !area) { alert('Fill all land details'); return; }
      const btn = event.target;
      btn.innerHTML = '<span class="spinner"></span>Estimating...';
      btn.disabled = true;
      try {
        const res = await fetch('/api/predict/land', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ state: state, area_acres: area, soil_type: +soil, irrigation: +irr, road_km: road })
        });
        const data = await res.json();
        show('land-result');
        id('land-result-val').textContent = '₹' + data.total_value.toLocaleString('en-IN');
        id('land-result-sub').textContent = '≈ ₹' + data.per_acre.toLocaleString('en-IN') + ' per acre';
      } catch (err) {
        alert("API Error: " + err.message);
      }
      btn.innerHTML = 'Estimate Value';
      btn.disabled = false;
    }
    """
    content = re.sub(r'function predictLandPrice\(\) \{.*?\n    \}', land_js, content, flags=re.DOTALL)

    # Weather API
    weather_js = """
    async function fetchWeather() {
      const city = v('weather-city').trim();
      if (!city) { alert('Enter a city name'); return; }
      const btn = event.target;
      btn.innerHTML = '...';
      try {
        const res = await fetch('/api/weather?city=' + encodeURIComponent(city));
        const data = await res.json();
        if(res.status !== 200) { alert(data.detail || 'City not found'); btn.innerHTML='Go'; return; }
        id('w-temp').textContent = data.temperature + '°C';
        id('w-desc').textContent = data.description + ` in ${data.city}`;
        id('w-hum').textContent = data.humidity + '%';
        id('w-wind').textContent = data.wind_speed + ' km/h';
        id('w-feels').textContent = data.feels_like + '°C';
        id('w-rain').textContent = data.rain_chance + '%';
        const advisory = document.getElementById('w-advisory');
        advisory.style.display = 'block';
        advisory.textContent = data.farming_advisory;
      } catch(err) {
        alert("API Error");
      }
      btn.innerHTML = 'Go';
    }
    """
    content = re.sub(r'async function fetchWeather\(\) \{.*?\n    \}', weather_js, content, flags=re.DOTALL)

    # Market API
    market_js = """
    let currentFilter = 'all';
    async function renderMarket(filter) {
      const tbody = id('market-tbody');
      try {
        const res = await fetch('/api/market/prices?category=' + filter);
        const data = await res.json();
        tbody.innerHTML = data.data.map(r => `
          <tr>
            <td style="font-weight:600">${r.crop}</td>
            <td><span class="badge badge-green" style="font-size:0.7rem;">${r.category}</span></td>
            <td style="color:var(--gray-300)">${r.market}</td>
            <td style="font-weight:700">₹${r.price}</td>
            <td>
              <div class="price-change ${r.change >= 0 ? 'price-up' : 'price-down'}">
                ${r.change >= 0 ? '▲' : '▼'} ${Math.abs(r.change)}%
              </div>
            </td>
            <td style="color:var(--gray-600);font-size:0.8rem">${r.updated}</td>
          </tr>
        `).join('');
      } catch(err) {
        tbody.innerHTML = "<tr><td colspan='6'>Failed to load market data</td></tr>";
      }
    }
    function filterMarket() {
      currentFilter = v('market-filter');
      renderMarket(currentFilter);
    }
    function refreshMarket() {
      renderMarket(currentFilter);
    }
    // Load initially
    document.addEventListener('DOMContentLoaded', () => { renderMarket('all'); });
    """
    content = re.sub(r'function renderMarket\(filter\).*?renderMarket\(\'all\'\);', market_js, content, flags=re.DOTALL)

    # Survey API
    survey_js = """
    async function submitSurvey() {
      const name = v('s-name'), village = v('s-village'), challenge = v('s-challenge'), crop = v('s-crop'), phone = v('s-phone');
      if (!name || !village || !challenge) { alert('Please fill all required fields'); return; }
      const btn = event.target;
      btn.innerHTML = '<span class="spinner"></span>Submitting...';
      btn.disabled = true;
      try {
        const res = await fetch('/api/survey/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name, village: village, challenge: challenge, crop: crop, phone_access: phone })
        });
        if(res.ok) {
          id('survey-success').style.display = 'block';
          btn.style.display = 'none';
          ['s-name','s-village','s-crop','s-challenge','s-phone'].forEach(f => {
            const el = id(f);
            if (el.tagName === 'SELECT') el.selectedIndex = 0;
            else el.value = '';
          });
        }
      } catch(err) {
        alert("Failed to submit");
        btn.innerHTML = 'Submit Feedback →';
        btn.disabled = false;
      }
    }
    """
    content = re.sub(r'function submitSurvey\(\) \{.*?\n    \}', survey_js, content, flags=re.DOTALL)

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print("Frontend Backend Integration Complete!")

if __name__ == "__main__":
    update_html()
