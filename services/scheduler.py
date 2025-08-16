# services/scheduler.py
from utils.timezones import ist_today_slots, to_utc_iso  # absolute import

def plan_today_slots(cfg_schedule):
    slots_ist = ist_today_slots(
        cfg_schedule["start"],
        cfg_schedule["interval_min"],
        cfg_schedule["count"],
        cfg_schedule["timezone"],
    )
    return [to_utc_iso(dt) for dt in slots_ist]

def pair_tweets_slots(tweets, utc_slots):
    plan = []
    for i, tw in enumerate(tweets):
        plan.append({
            "text": tw["text"],
            "source": tw.get("source", ""),
            "schedule-date": utc_slots[i] if i < len(utc_slots) else "next-free-slot",
        })
    return plan
