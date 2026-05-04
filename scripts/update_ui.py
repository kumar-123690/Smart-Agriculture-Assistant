import re
import os
import sys

def main():
    filepath = r"c:\cspproject\index.html"
    if not os.path.exists(filepath):
        print("File not found")
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject Lucide script
    if "<script src=\"https://unpkg.com/lucide@latest\"></script>" not in content:
        content = content.replace("</head>", "  <script src=\"https://unpkg.com/lucide@latest\"></script>\n</head>")

    # 2. Add Spotlight and Form Floating CSS
    custom_css = """
    /* =============================================
       NEW UI UPGRADES (Nav Pill, Spotlight, Forms)
    ============================================= */
    /* Floating Pill Nav */
    nav {
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 90%;
      max-width: 1100px;
      border-radius: 99px;
      background: rgba(10,46,26,0.7);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(255,255,255,0.08);
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
      padding: 0 24px;
      height: 64px;
      z-index: 1000;
    }
    #hero {
      padding-top: 100px; /* offset for pill nav */
    }

    /* Form Floating Labels */
    .form-group {
      position: relative;
      margin-bottom: 24px;
    }
    .form-input, .form-select {
      width: 100%;
      padding: 16px 16px 8px;
      background: rgba(10,46,26,0.6);
      border: 1px solid rgba(46,204,113,0.2);
      border-radius: var(--radius-sm);
      color: var(--white);
      font-size: 0.95rem;
      transition: all 0.2s ease;
    }
    .form-label {
      position: absolute;
      top: 14px;
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
      top: 4px;
      left: 16px;
      font-size: 0.65rem;
      color: var(--green-400);
      font-weight: 600;
    }
    .form-input::placeholder {
      color: transparent; /* hide placeholder for floating label to work */
    }
    .form-input:focus {
      border-color: var(--green-500);
      background: rgba(10,46,26,0.9);
      box-shadow: 0 4px 16px rgba(46,204,113,0.15);
    }

    /* Spotlight Card Effect */
    .feature-card, .tool-card, .scheme-card, .tech-card {
      position: relative;
      overflow: hidden;
      background: rgba(15,69,38,0.5);
      border: 1px solid rgba(46,204,113,0.15);
      backdrop-filter: blur(10px);
      z-index: 1;
    }
    .spotlight {
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity 0.3s;
      background: radial-gradient(600px circle at var(--x, 50%) var(--y, 50%), rgba(46,204,113,0.15), transparent 40%);
      z-index: -1;
      pointer-events: none;
    }
    .feature-card:hover .spotlight, .tool-card:hover .spotlight, .scheme-card:hover .spotlight, .tech-card:hover .spotlight {
      opacity: 1;
    }

    /* Lucide Icon adjustments */
    .lucide {
      width: 1em;
      height: 1em;
      vertical-align: -0.125em;
    }
    .feature-icon .lucide { width: 32px; height: 32px; stroke-width: 1.5; color: var(--green-400); }
    .scheme-icon .lucide { width: 32px; height: 32px; stroke-width: 1.5; color: var(--green-400); }
    .tech-emoji .lucide { width: 32px; height: 32px; stroke-width: 1.5; color: var(--green-400); }
    .icon .lucide { width: 24px; height: 24px; stroke-width: 1.5; color: var(--green-400); }
    .nav-logo .lucide { width: 28px; height: 28px; stroke-width: 2; color: var(--green-400); }
    .upload-icon .lucide { width: 48px; height: 48px; stroke-width: 1; color: var(--green-400); }
    .weather-icon .lucide { width: 64px; height: 64px; stroke-width: 1; color: var(--green-400); }

    /* Hero Background Override */
    #hero::before {
      background: url('hero_bg.png') center/cover no-repeat !important;
      opacity: 0.35;
      filter: contrast(1.1) brightness(0.9);
      mix-blend-mode: overlay;
    }
    """
    if "/* Floating Pill Nav */" not in content:
        content = content.replace("</style>", custom_css + "\n  </style>")

    # Remove old nav CSS to avoid conflicts
    content = re.sub(r'nav\s*\{\s*position: fixed;\s*top: 0;.*?justify-content: space-between;\s*\}', '', content, flags=re.DOTALL)

    # 3. Swap inputs and labels for the floating label trick
    # We replace: <label...>...</label> \n <input...> with <input... placeholder=" "> \n <label...>...</label>
    # Find all groups
    content = re.sub(
        r'(<div class="form-group">\s*)(<label class="form-label">.*?</label>)\s*(<input[^>]+class="form-input"[^>]*>)',
        lambda m: m.group(1) + m.group(3).replace('placeholder="', 'placeholder=" " data-ph="') + '\n              ' + m.group(2),
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'(<div class="form-group">\s*)(<label class="form-label">.*?</label>)\s*(<select[^>]+class="form-select"[^>]*>)',
        r'\1\3\n              \2',
        content,
        flags=re.DOTALL
    )

    # Add spotlight div to cards
    card_classes = ["feature-card", "tool-card", "scheme-card", "tech-card", "weather-card", "survey-card"]
    for cls in card_classes:
        content = re.sub(rf'(<div class="{cls}"[^>]*>)', r'\1\n          <div class="spotlight"></div>', content)

    # 4. Replace emojis with Lucide
    emoji_map = {
        '🌿': 'leaf', '🌾': 'wheat', '🌡️': 'thermometer', '🤖': 'bot', '📈': 'trending-up', '💰': 'indian-rupee',
        '🔬': 'microscope', '🏡': 'home', '⛅': 'cloud-sun', '📊': 'bar-chart-2', '🧪': 'test-tube', '📋': 'clipboard-list',
        '🌐': 'globe', '📷': 'camera', '⚛️': 'atom', '🐍': 'file-code', '🧠': 'brain', '🌲': 'trees', '🐬': 'database',
        '☁️': 'cloud', '🐼': 'sheet', '🚀': 'rocket', '💵': 'banknote', '💧': 'droplet', '📱': 'smartphone',
        '🌱': 'sprout', '🌽': 'carrot', '🥜': 'bean', '🧅': 'circle', '🍅': 'apple', '☕': 'coffee', '🍋': 'citrus',
        '🥭': 'apple', '🫘': 'bean', '🌶️': 'flame', '✅': 'check-circle', '⚠️': 'alert-triangle', '🌧️': 'cloud-rain'
    }
    for emoji, icon in emoji_map.items():
        content = content.replace(emoji, f'<i data-lucide="{icon}"></i>')

    # 5. Inject JS logic
    js_code = """
    // Initialize Lucide icons
    lucide.createIcons();

    // Spotlight effect logic
    document.querySelectorAll('.feature-card, .tool-card, .scheme-card, .tech-card').forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty('--x', x + 'px');
        card.style.setProperty('--y', y + 'px');
      });
    });
    """
    if "lucide.createIcons();" not in content:
        content = content.replace("</body>", f"  <script>\n{js_code}\n  </script>\n</body>")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print("UI Updates Applied Successfully!")

if __name__ == "__main__":
    main()
