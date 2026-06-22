from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import hashlib
import secrets
from typing import List

# Welcome note with participant name
WELCOME_NOTE = "Welcome to the token generator demo. Participant: Harini Sanagapalli"

app = FastAPI(
    title="Token Generator API",
    description=f"A small FastAPI app that generates pseudorandom tokens and checksums.\n{WELCOME_NOTE}",
)

# Create a Pydantic model for the POST JSON body
# (GitHub Copilot prompt: "Create a Pydantic model named TextRequest with a single field 'text' of type str")
class TextRequest(BaseModel):
    text: str


def generate(text: str, count: int = 1) -> List[str]:
    """
    Generate `count` pseudorandom tokens derived from `text`.

    Returns a list of tokens. Each token includes a short checksum prefix so it's easy to correlate
    tokens with the input text while remaining unpredictable (uses secrets.token_hex).
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string")

    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    tokens = [f"{checksum[:8]}-{secrets.token_hex(8)}" for _ in range(max(1, count))]
    return tokens


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve a minimal HTML page with a form to submit text and display generated tokens."""
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Token Generator</title>
        <style>
          body {{ font-family: Arial, sans-serif; max-width: 680px; margin: 2rem auto; }}
          textarea {{ width: 100%; height: 6rem; }}
          pre {{ background: #f6f8fa; padding: 1rem; border-radius: 6px; }}
        </style>
      </head>
      <body>
        <h1>Token Generator</h1>
        <p>{WELCOME_NOTE}</p>
        <form id="form">
          <label for="text">Text</label><br />
          <textarea id="text" name="text"></textarea><br />
          <label for="count">Token count</label>
          <input id="count" name="count" type="number" value="1" min="1" style="width:5rem" />
          <button type="submit">Generate</button>
        </form>
        <h2>Result</h2>
        <pre id="result">(no result yet)</pre>

        <script>
          document.getElementById('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = document.getElementById('text').value;
            const count = parseInt(document.getElementById('count').value) || 1;

            // Call the JSON POST endpoint
            const resp = await fetch('/tokens?count=' + encodeURIComponent(count), {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text })
            });
            const body = await resp.json();
            document.getElementById('result').textContent = JSON.stringify(body, null, 2);
          });
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/token")
async def token_endpoint(text: str = "default"):
    """Existing single-token endpoint (keeps compatibility). Returns a single token for provided text."""
    try:
        tokens = generate(text, count=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid text provided")
    return {"token": tokens[0], "checksum": hashlib.sha256(text.encode('utf-8')).hexdigest()}


# Create a FastAPI endpoint to accept POST JSON with a single field 'text'
@app.post("/tokens")
async def tokens_endpoint(req: TextRequest, count: int = 1):
    """
    Accepts JSON body {"text": "..."} and query parameter `count` (optional).
    Returns the checksum of the text and a list of `count` tokens.

    Example request:
      POST /tokens?count=3
      { "text": "hello" }

    Response format:
      { "checksum": "...", "tokens": ["..."] }
    """
    text = req.text
    if not text:
        raise HTTPException(status_code=400, detail="text must be a non-empty string")

    checksum = hashlib.sha256(text.encode('utf-8')).hexdigest()
    tokens = generate(text, count=count)
    return JSONResponse({"checksum": checksum, "tokens": tokens})


# This module can be run with: uvicorn main:app --reload --port 8000

