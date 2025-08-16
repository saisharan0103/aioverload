import yaml
from .gemini_client import call_gemini_json

def fetch_top10(model, fetch_prompt_path):
    prm = yaml.safe_load(open(fetch_prompt_path, encoding="utf-8"))
    data = call_gemini_json(model, prm["system"], prm["user"])
    items = data.get("items", [])
    if len(items) != 10:
        raise ValueError(f"Expected 10 items, got {len(items)}")
    # minimal sanitize
    for it in items:
        it["title"] = it["title"].strip()[:160]
        it["summary"] = it["summary"].strip()[:160]
    return {"items": items}
