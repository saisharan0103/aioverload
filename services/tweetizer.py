import yaml, json
from .gemini_client import call_gemini_json

def make_tweets(model, tweetizer_prompt_path, items, tags):
    prm = yaml.safe_load(open(tweetizer_prompt_path, encoding="utf-8"))
    user = prm["user"].replace("{{ITEMS_JSON}}", json.dumps(items, ensure_ascii=False)) \
                      .replace("{{TAGS}}", " ".join(tags))
    data = call_gemini_json(model, prm["system"], user)
    tweets = data.get("tweets", [])[:10]
    for t in tweets:
        # hard limit
        if len(t["text"]) > 280:
            t["text"] = t["text"][:277] + "..."
    return tweets
