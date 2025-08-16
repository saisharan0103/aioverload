import os, json, uuid, datetime as dt
def ensure_dir(p): os.makedirs(p, exist_ok=True)
def run_id(): return dt.datetime.utcnow().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
def write_json(path, data):
    ensure_dir(os.path.dirname(path)); 
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
def append_jsonl(path, obj):
    ensure_dir(os.path.dirname(path))
    with open(path, "a", encoding="utf-8") as f: f.write(json.dumps(obj, ensure_ascii=False) + "\n")
