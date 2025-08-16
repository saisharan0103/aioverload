import os, json, requests
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

class GeminiJSONError(RuntimeError): pass

def _model(name:str, system_msg:str):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    return genai.GenerativeModel(
        model_name=name,
        system_instruction=system_msg,  # <-- put system here
        generation_config={"response_mime_type":"application/json","temperature":0.5},
    )

@retry(reraise=True, stop=stop_after_attempt(6),
       wait=wait_random_exponential(multiplier=1, max=60),
       retry=retry_if_exception_type(ResourceExhausted))
def _sdk_call(name, system_msg, user_msg, use_web):
    m=_model(name, system_msg)
    kwargs={"tools":[{"google_search_retrieval":{}}]} if use_web else {}
    # contents must NOT include a system role
    return m.generate_content([{"role":"user","parts":[user_msg]}], **kwargs)

def _rest_call(name, system_msg, user_msg, use_web)->str:
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent?key={os.environ['GEMINI_API_KEY']}"
    payload={
      "systemInstruction": {"parts":[{"text": system_msg}]},  # <-- systemInstruction here
      "contents": [ {"role":"user","parts":[{"text": user_msg}]} ],
      "generationConfig": {"responseMimeType":"application/json","temperature":0.5}
    }
    if use_web: payload["tools"]=[{"googleSearchRetrieval":{}}]
    r=requests.post(url,json=payload,timeout=90)
    if r.status_code==429: raise requests.RequestException("429")
    r.raise_for_status()
    data=r.json()
    text=data.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","")
    if not text: raise GeminiJSONError("REST empty")
    return text

def call_gemini_json(model_name, system_msg, user_msg, *, use_web_search=True)->dict:
    try:
        resp=_sdk_call(model_name, system_msg, user_msg, use_web_search)
        text=(resp.text or "").strip()
    except ResourceExhausted:
        text=_rest_call(model_name, system_msg, user_msg, use_web_search)
    s,e=text.find("{"),text.rfind("}")
    if s==-1 or e==-1: raise GeminiJSONError("Non-JSON response:\n"+text[:500])
    return json.loads(text[s:e+1])
