import os, base64, json
import anthropic
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

app = FastAPI(title="VisionIQ — AI Image Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

ALLOWED = {"image/jpeg","image/jpg","image/png","image/webp","image/gif","image/bmp"}
MAX_SIZE = 20 * 1024 * 1024

PROMPT = """Analyze the uploaded image in detail. Determine whether it contains charts, tables,
screenshots, dashboards, text, drawings, diagrams, photos, reports, or business content.

Provide a comprehensive analysis in the following exact JSON structure
(respond ONLY with valid JSON — no markdown, no code fences):

{
  "image_type": "Brief description of what type of image this is",
  "executive_summary": "2-3 sentence overview of the image and its main purpose",
  "key_findings": ["Finding 1 — use **bold** for important terms", "Finding 2", "Finding 3"],
  "detailed_analysis": "Comprehensive explanation of all visible information. Use **bold** for KPIs, metrics, key values.",
  "metrics": [{"label": "Metric Name", "value": "Value", "context": "Brief context"}],
  "trends_and_patterns": ["Trend 1", "Trend 2"],
  "insights": ["Insight 1", "Insight 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "highlights": {
    "kpis": ["kpi1","kpi2"],
    "warnings": ["warning1"],
    "dates": ["date1"],
    "percentages": ["12%","45%"]
  }
}

Use **bold** around all key business terms, numbers, percentages, dates, and KPIs."""


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, f"Unsupported type: {file.content_type}")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(400, "File exceeds 20 MB limit.")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured.")

    mt = file.content_type
    if mt in ("image/jpg", "image/bmp"):
        mt = "image/jpeg" if mt == "image/jpg" else "image/png"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mt, "data": base64.standard_b64encode(data).decode()}},
                {"type": "text",  "text": PROMPT}
            ]}]
        )
        raw = msg.content[0].text.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        try:
            analysis = json.loads(raw)
        except Exception:
            analysis = {
                "image_type": "Image", "executive_summary": raw[:500],
                "key_findings": ["See detailed analysis"], "detailed_analysis": raw,
                "metrics": [], "trends_and_patterns": [], "insights": [], "recommendations": [],
                "highlights": {"kpis":[], "warnings":[], "dates":[], "percentages":[]}
            }
        return JSONResponse({"success": True, "filename": file.filename, "file_size": len(data), "analysis": analysis})
    except anthropic.APIError as e:
        raise HTTPException(500, f"Claude API error: {e}")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")


# Serve the frontend if index.html is in the same directory
if os.path.exists("index.html"):
    @app.get("/")
    async def serve_frontend():
        return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)
