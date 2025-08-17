# utils/gemini_rest.py
import os, json, time, random, requests

API_KEY = os.environ["GEMINI_API_KEY"]

def _backoff(attempt: int) -> None:
    time.sleep(min(60, 2**attempt + random.uniform(0, 3)))

def call_gemini_json(model: str, system_msg: str, user_msg: str, *, use_web: bool=True) -> dict:
    """Calls Gemini REST endpoint and returns a parsed JSON object from the model's text output."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    body = {
        "systemInstruction": {"parts": [{"text": system_msg}]},
        "contents": [{"role": "user", "parts": [{"text": user_msg}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.5},
    }
    if use_web:
        body["tools"] = [{"googleSearchRetrieval": {}}]

    last_err = None
    for attempt in range(6):  # retry on 429/5xx
        r = requests.post(url, json=body, timeout=90)
        if r.status_code in (429, 500, 502, 503, 504):
            last_err = r
            _backoff(attempt)
            continue
        r.raise_for_status()
        data = r.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        s, e = text.find("{"), text.rfind("}")
        if s == -1 or e == -1:
            raise RuntimeError(f"Gemini returned non-JSON text: {text[:400]}")
        return json.loads(text[s:e+1])

    raise RuntimeError(f"Gemini REST failed after retries: {getattr(last_err,'status_code',None)} {getattr(last_err,'text','')[:200]}")
