Tools & AI Usage: Built using Python, FastAPI, and the Google GenAI SDK. Drafted code structure and README documentation using Gemini as a collaborative pair-programming assistant.



What it is: Clean, structured documentation displaying your API routes, request bodies, and JSON response models.
# Git Request Triage Machine 🛠️

People on our team send requests in messy, rushed ways—texts, random one-liners, or long emails with multiple asks. Someone usually has to read through all that noise to figure out what's actually going on. 

I built a small tool that automates that first read using Gemini so a developer gets something structured and useful right away.

## 🚀 Live Demo
[Paste your Render URL here after deploying!]

---

## What I built and why I made those choices
* **FastAPI + Web UI:** I wanted something super quick to spin up and test, so I made a lightweight Python backend with a single-page HTML frontend. 
* **Gemini & Pydantic:** I used `gemini-2.5-flash` with Pydantic structured outputs. Instead of letting the AI just spit out regular text, the schema forces it to return clean, predictable JSON every single time (with fields like intent, priority, summary, and action steps).

---

## First attempt vs. what I changed
* **First attempt:** I just wrote a basic prompt telling Gemini, *"Hey, look at this message and return JSON."* 
* **What failed:** Half the time, the model would wrap the JSON in markdown code blocks (` ```json `) or add filler text at the beginning like *"Sure, here is your data!"*, which immediately broke my Python JSON parser.
* **What I changed:** I switched to native Pydantic schema enforcement via the Google GenAI SDK. That completely solved the problem because the API guarantees the output matches my structure before it even reaches my code.

---

## Where it still breaks
* **Context starvation:** If someone sends a super vague message like *"Hey the login button is broken fix pls"*, the tool can flag it as a bug and ask good clarifying questions, but it still has no way of knowing *which* app, environment, or repository they're talking about without more background info.
* **Multi-intent messages:** If someone crams two completely different requests into one sentence (e.g., *"Fix the checkout bug and also update the dark mode styles"*), the model tends to mush them together into one summary instead of cleanly splitting them into two separate tasks.

---

## How I'd know if it got worse over time
If I wanted to track whether this tool was degrading over a few weeks or months, I'd look at:
1. **The Ambiguity Rate:** Tracking how often requests get flagged as `is_ambiguous = True`. If that number suddenly spikes, it usually means either people's messaging habits got worse or a new feature is confusing everyone.
2. **API Error Logs:** Monitoring backend 500 errors to see if model updates or schema changes ever break the parsing pipeline.

---

## Running it locally
1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt

Set your Gemini API key:

Bash
export GEMINI_API_KEY="your-key-here"
Run it:

Bash
python3 -m uvicorn main:app --reload

---

### Step 2: Save and Push to GitHub
Press **`Ctrl + S`** (or `Cmd + S` on Mac) to save the `README.md` file.

Then, run this command in your Codespaces terminal:

```bash
git add README.md main.py requirements.txt
git commit -m "Add README and ensure all core files are committed"
git push origin main

## 📝 Example Inputs & Outputs

### 1. Messy Bug Request (Valid)
* **Input:** `"hey checkout page gives error 500 when clicking pay now on mobile safari fix asap"`
* **Output:**
  ```json
  {
    "intent": "bug",
    "priority": "urgent",
    "summary": "500 error on checkout payment via Mobile Safari.",
    "actionable_steps": ["Check server logs for payment error", "Reproduce on Mobile Safari"],
    "routing_team": "backend",
    "is_ambiguous": false
  }

Input: "the lights are off pls fix"
Output:
{
  "intent": "bug",
  "priority": "low",
  "summary": "User reported lights being off without specifying location, office, or UI context.",
  "actionable_steps": [],
  "routing_team": "facilities",
  "is_ambiguous": true,
  "clarifying_questions": ["Is this referring to physical office lighting or a UI theme issue?"]
}

