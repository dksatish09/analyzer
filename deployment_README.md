# VisionIQ — AI Image Analyzer
## Deployment Guide

---

## Option 1 — Open Directly in Browser (zero setup)

1. Open `index.html` in any modern browser.
2. The app calls the **Claude API directly from your browser**.
   - It works immediately — no server needed.
   - Note: the Anthropic API key is handled by the claude.ai proxy in artifact mode.
     For standalone use, open `index.html`, find the `BACKEND_URL` constant and ensure it is `""`.

---

## Option 2 — Full Stack (FastAPI + Claude API)

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Place index.html in the same folder as main.py
#    Then run:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000

### Point Frontend at Backend

In `index.html`, find this line near the top of the `<script>` block:

```js
const BACKEND_URL = ""; // Set to your FastAPI URL e.g. "https://your-app.onrender.com"
```

Change it to your server URL:
```js
const BACKEND_URL = "http://localhost:8000";
```

---

## Deploy to Render (free tier)

1. Push these files to a GitHub repo:
   - `main.py`
   - `requirements.txt`
   - `index.html`

2. Go to https://render.com → New → Web Service

3. Settings:
   | Field | Value |
   |---|---|
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Environment Variable | `ANTHROPIC_API_KEY` = your key |

4. After deploy, your URL will be `https://your-app.onrender.com`

5. Update `BACKEND_URL` in `index.html` to that URL, push again.

---

## File Structure

```
your-project/
├── index.html          ← Frontend (React, single file)
├── main.py             ← FastAPI backend
├── requirements.txt    ← Python deps
└── README.md
```

---

## Supported Image Types
JPG · JPEG · PNG · WEBP · GIF · BMP (max 20 MB)

## Analysis Sections
- Executive Summary
- Key Findings
- Detailed Analysis
- Metrics (auto-extracted)
- Trends & Patterns
- Insights
- Recommendations
- Highlighted Terms (KPIs, dates, percentages, warnings)
