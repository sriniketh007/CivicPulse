import json
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables (like GEMINI_API_KEY)
load_dotenv()

app = FastAPI(title="CivicPulse AI Engine")

# Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client
ai_client = genai.Client()
MODEL_NAME = 'gemini-2.5-flash' # Gemini 2.5 Flash

# --- Database Setup ---
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = str(BASE_DIR / "civicpulse.db")

def init_sqlite_db():
    """Initializes the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citizen_reports (
            id TEXT PRIMARY KEY,
            query_topic TEXT,
            input_text TEXT,
            category TEXT,
            sentiment TEXT,
            intent TEXT,
            go_for_it_score INTEGER,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Ensure table exists when the server starts up
init_sqlite_db()


# --- API Endpoints ---

@app.post("/api/citizen/classify-text")
async def classify_and_save_text(
    text: str = Form(...),
    query_topic: Optional[str] = Form(default="General Community Needs")
):
    try:
        # 1. Ask Gemini to analyze the text
        prompt = f"""
        You are CivicPulse AI, an intelligent public governance engine.
        Context / Inquiry: "{query_topic}"
        Citizen Input: "{text}"

        Analyze the input and return ONLY a valid JSON object matching this schema:
        {{
          "category": "Roads & Transit | Water & Sanitation | Healthcare | Public Safety | Energy | Education | Other",
          "sentiment": "Positive | Neutral | Negative",
          "intent": "Support | Opposition | Grievance | Suggestion",
          "goForItScore": 85,
          "summary": "1-sentence summary"
        }}
        """

        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        # 2. Clean the AI response (strips out markdown code blocks if the AI includes them)
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # 3. Convert the cleaned text into a Python dictionary
        analysis = json.loads(raw_text)
        
        # 4. Generate a unique ID for this report
        report_id = str(uuid.uuid4())

        # 5. Save the data to the SQLite Database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO citizen_reports (id, query_topic, input_text, category, sentiment, intent, go_for_it_score, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            query_topic,
            text,
            analysis.get("category"),
            analysis.get("sentiment"),
            analysis.get("intent"),
            analysis.get("goForItScore"),
            analysis.get("summary")
        ))
        conn.commit()
        conn.close()

        # 6. Send a success response back to the frontend
        return {
            "success": True,
            "message": "Report analyzed and saved successfully",
            "report_id": report_id,
            "data": analysis # Returning the data so the frontend can immediately display it if needed
        }

    except Exception as e:
        # Print the exact error to the backend terminal to help with debugging
        print(f"\n--- CRASH REASON --- \n{str(e)}\n--------------------\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/citizen/reports")
async def get_all_reports():
    """Retrieves all saved reports for the Government Dashboard."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Enables us to access columns by name
        cursor = conn.cursor()
        
        # Fetch all reports, newest first
        cursor.execute("SELECT * FROM citizen_reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        # Convert the SQL rows into a list of dictionaries for React
        reports = [dict(row) for row in rows]
        
        return {"success": True, "count": len(reports), "data": reports}

    except Exception as e:
        print(f"\n--- DATABASE ERROR --- \n{str(e)}\n--------------------\n")
        raise HTTPException(status_code=500, detail=str(e))


# Serve the built React frontend from dist/ (only in production)
dist_dir = BASE_DIR / "dist"
if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # Don't intercept /api routes
        index = dist_dir / "index.html"
        return FileResponse(str(index))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)