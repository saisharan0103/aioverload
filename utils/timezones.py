from datetime import datetime, timedelta
import pytz

def ist_today_slots(start_hm: str, interval_min: int, count: int, tz_name="Asia/Kolkata"):
    tz = pytz.timezone(tz_name)
    today = datetime.now(tz).replace(hour=int(start_hm[:2]), minute=int(start_hm[3:5]),
                                     second=0, microsecond=0)
    slots = [today + timedelta(minutes=i*interval_min) for i in range(count)]
    return slots

def to_utc_iso(dt_aware):
    return dt_aware.astimezone(pytz.UTC).isoformat().replace("+00:00", "Z")
