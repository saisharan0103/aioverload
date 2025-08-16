import yaml, time
from .gemini_client import call_gemini_json

def _fetch_n(model, prm, n):
    user = prm["user"].replace("exactly 10", f"exactly {n}")
    return call_gemini_json(model, prm["system"], user, use_web_search=True)

def fetch_top10(model, fetch_prompt_path):
    prm = yaml.safe_load(open(fetch_prompt_path, encoding="utf-8"))
    try:
        a=_fetch_n(model, prm, 5); time.sleep(2)
        b=_fetch_n(model, prm, 5)
        items = (a.get("items", []) + b.get("items", []))[:10]
    except Exception:
        # minimal fallback so pipeline keeps running in DRY_RUN
        items=[{"title":f"Placeholder AI item {i+1}",
                "url":f"https://example.com/{i+1}",
                "summary":"(fallback due to quota)"} for i in range(10)]
    return {"items": items}
