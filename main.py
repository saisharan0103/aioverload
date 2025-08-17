import os, yaml
from utils.logger import get_logger
from utils.storage import run_id, write_json, append_jsonl
from services.fetcher import fetch_top10
from services.tweetizer import make_tweets
from services.scheduler import plan_today_slots, pair_tweets_slots
from services.typefully import schedule_draft

log = get_logger("main")
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"

def load_yaml(path):
    return yaml.safe_load(open(path, encoding="utf-8"))

def _show_both(utc_str: str) -> str:
    """Return both UTC and IST time in log for clarity."""
    from utils.timezones import to_ist_str
    return f"{utc_str} / {to_ist_str(utc_str)}"

def run():
    rid = run_id()
    cfg_acc = load_yaml("config/accounts.yaml")
    cfg_sch = load_yaml("config/schedule.yaml")
    cfg_set = load_yaml("config/settings.yaml")

    log.info(f"run_id={rid} dry_run={DRY_RUN}")

    # 1. Fetch trending content
    fetched = fetch_top10(cfg_set["model"], "prompts/fetch_top10.yaml")
    write_json(f"runs/{rid}/fetch.json", fetched)

    # 2. Generate tweets
    tweets = make_tweets(
        cfg_set["model"],
        "prompts/tweetizer.yaml",
        fetched["items"],
        cfg_set["tags"],
    )
    write_json(f"runs/{rid}/tweets.json", {"tweets": tweets})

    # 3. Plan today’s slots
    utc_slots = plan_today_slots(cfg_sch)
    plan = pair_tweets_slots(tweets, utc_slots)

    # 4. Schedule per account
    for acc in cfg_acc["accounts"]:
        if not acc.get("enabled"):
            log.info(f"skip account={acc['name']}")
            continue

        key_env = acc["typefully_key_env"]
        results = []

        for i, p in enumerate(plan):
            content = p["text"]
            src = p.get("source")
            if src and src not in content:
                content += f"\n\n{src}"

            # hard guard: empty & length (280 + URL slack)
            ctrim = (content or "").strip()
            if not ctrim:
                log.error(f"SKIP empty content at idx={i}")
                continue
            if len(ctrim) > 320:
                ctrim = ctrim[:317] + "..."

            sched = p["schedule-date"]
            log.info(f"DEBUG payload preview idx={i+1}: len={len(ctrim)} sched={sched}")

            if DRY_RUN:
                status, resp = 0, {"id": "dry-run"}
            else:
                resp, status = schedule_draft(key_env, ctrim, sched)

            item = {
                "run_id": rid,
                "account": acc["name"],
                "utc_time": sched,
                "status": status,
                "resp_id": resp.get("id"),
                "text": ctrim[:140],
            }
            append_jsonl(cfg_set["logs_path"], item)
            results.append(item)
            log.info(
                f"{acc['name']} [{i+1}/{len(plan)}] -> {_show_both(sched)} (status={status})"
            )

        write_json(f"runs/{rid}/scheduled_{acc['name']}.json", results)

if __name__ == "__main__":
    run()
