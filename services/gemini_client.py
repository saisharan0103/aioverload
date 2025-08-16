import os, json
import google.generativeai as genai

def _model(model_name: str):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel(
        model_name,
        generation_config={"response_mime_type": "application/json"}  # force JSON
    )

def call_gemini_json(model_name: str, system_msg: str, user_msg: str) -> dict:
    model = _model(model_name)
    resp = model.generate_content(
        [{"role": "system", "parts": [system_msg]},
         {"role": "user", "parts": [user_msg]}],
        tools=[{"google_search_retrieval": {}}]  # enable web
    )
    text = (resp.text or "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return JSON.")
    return json.loads(text[start:end+1])
