import os, json
import google.generativeai as genai

class GeminiJSONError(RuntimeError): pass

def _model(model_name: str):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # Force JSON out & allow long responses if needed
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.7,
        }
    )

def call_gemini_json(model_name: str, system_msg: str, user_msg: str, *, use_web_search: bool = True) -> dict:
    """
    Calls Gemini with optional Google web search grounding enabled.
    Returns parsed JSON (raises if JSON not found).
    """
    model = _model(model_name)
    parts = [
        {"role": "system", "parts": [system_msg]},
        {"role": "user",   "parts": [user_msg]},
    ]

    kwargs = {}
    if use_web_search:
        # Enable Google Search Retrieval tool (web grounding)
        kwargs["tools"] = [{"google_search_retrieval": {}}]

    resp = model.generate_content(parts, **kwargs)
    text = (resp.text or "").strip()
    # Extract strict JSON object from text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise GeminiJSONError("Gemini did not return JSON. Raw text:\n" + text[:500])
    return json.loads(text[start:end+1])

# --- Optional: direct REST endpoint variant (if you prefer REST over SDK) ---

import requests

def call_gemini_json_rest(model_name: str, system_msg: str, user_msg: str, *, use_web_search: bool = True) -> dict:
    """
    Direct REST call to the Generative Language API with web search grounding.
    Endpoint includes your API key via query param. Returns parsed JSON.
    """
    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {"role": "system", "parts": [{"text": system_msg}]},
            {"role": "user",   "parts": [{"text": user_msg}]}
        ],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }
    if use_web_search:
        payload["tools"] = [{"googleSearchRetrieval": {}}]  # REST uses camelCase
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise GeminiJSONError("Unexpected REST response: " + json.dumps(data)[:500])
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise GeminiJSONError("REST: Gemini did not return JSON. Raw text:\n" + text[:500])
    return json.loads(text[start:end+1])
