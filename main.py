import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="Git Request Triage Machine")

# Initialize Gemini Client (reads GEMINI_API_KEY from environment variables automatically)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Define the Structured Output Schema using Pydantic
class TriageResult(BaseModel):
    intent: str = Field(description="Category of request: bug, feature_request, question, access_request, non_actionable, or ambiguous")
    priority: str = Field(description="Priority level: low, medium, high, or urgent")
    summary: str = Field(description="A clean, one-sentence developer-friendly translation of the request")
    actionable_steps: list[str] = Field(description="List of steps a developer should take to handle this")
    routing_team: str = Field(description="Suggested team: frontend, backend, devops, product, support, or general")
    is_ambiguous: bool = Field(description="True if important details are missing, false otherwise")
    clarifying_questions: list[str] = Field(description="Questions to ask the sender back if details are missing")

class RequestPayload(BaseModel):
    raw_message: str

@app.post("/triage")
def triage_request(payload: RequestPayload):
    if not payload.raw_message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    prompt = f"""
    Analyze the following raw team message and triage it for software developers.
    Extract the intent, priority, summary, steps, routing team, ambiguity, and clarifying questions.
    
    Raw Message: "{payload.raw_message}"
    """

    try:
        # Using gemini-2.5-flash with native Pydantic schema validation
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TriageResult,
                temperature=0.1,
            ),
        )
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Git Request Triage Machine</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; color: #333; margin: 0; padding: 40px; }
            .container { max-width: 700px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
            h1 { margin-top: 0; color: #1a202c; font-size: 24px; }
            textarea { width: 100%; height: 100px; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 15px; resize: vertical; box-sizing: border-box; }
            button { background: #3182ce; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 6px; cursor: pointer; margin-top: 10px; font-weight: 600; }
            button:hover { background: #2b6cb0; }
            .result { margin-top: 25px; background: #edf2f7; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-family: monospace; font-size: 13px; display: none; }
            .loading { color: #718096; margin-top: 10px; display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛠️ Git Request Triage Machine</h1>
            <p>Paste a messy team message below to see how the engine categorizes and structures it for developers.</p>
            <textarea id="messageInput" placeholder="e.g., hey app is down fix pls or can we add dark mode..."></textarea>
            <br>
            <button onclick="triageMessage()">Triage Request</button>
            <div id="loading" class="loading">Processing request through Gemini...</div>
            <div id="resultBox" class="result"></div>
        </div>

        <script>
            async function triageMessage() {
                const text = document.getElementById('messageInput').value;
                const resultBox = document.getElementById('resultBox');
                const loading = document.getElementById('loading');
                
                if (!text.trim()) {
                    alert('Please enter a message first.');
                    return;
                }

                loading.style.display = 'block';
                resultBox.style.display = 'none';

                try {
                    const response = await fetch('/triage', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ raw_message: text })
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultBox.textContent = JSON.stringify(data, null, 2);
                        resultBox.style.display = 'block';
                    } else {
                        resultBox.textContent = "Error: " + (data.detail || "Unknown error");
                        resultBox.style.display = 'block';
                    }
                } catch (err) {
                    resultBox.textContent = "Network Error: " + err.message;
                    resultBox.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """
