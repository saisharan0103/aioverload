# services/fetcher.py
import yaml, time, random
from utils.gemini_rest import call_gemini_json

def _fetch_n(model, prm, n):
    user = prm["user"].replace("exactly 10", f"exactly {n}")
    return call_gemini_json(model, prm["system"], user, use_web=True)

def fetch_top10(model, fetch_prompt_path):
    prm = yaml.safe_load(open(fetch_prompt_path, encoding="utf-8"))
    # Split to reduce 429s; small jitter between calls
    a = _fetch_n(model, prm, 5); time.sleep(3 + random.random())
    b = _fetch_n(model, prm, 5)
    items = (a.get("items", []) + b.get("items", []))[:10]

    if len(items) != 10:
        raise ValueError(f"Expected 10 items, got {len(items)}")

    # basic trim
    for it in items:
        it["title"] = it["title"].strip()[:160]
        it["summary"] = it["summary"].strip()[:160]
        if not it.get("url"):
            raise ValueError("Item missing URL")

    return {"items": items}
