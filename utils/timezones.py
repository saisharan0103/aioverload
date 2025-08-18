from datetime import datetime, timedelta
import pytz

def ist_today_slots(start_hm: str, interval_min: int, count: int, tz_name="Asia/Kolkata"):
    tz = pytz.timezone(tz_name)
    today = datetime.now(tz).replace(
        hour=int(start_hm[:2]), minute=int(start_hm[3:5]), second=0, microsecond=0
    )
    return [today + timedelta(minutes=i * interval_min) for i in range(count)]

def to_utc_iso(dt_aware):
    return dt_aware.astimezone(pytz.UTC).isoformat().replace("+00:00", "Z")

def to_ist_str(utc_iso: str, tz_name="Asia/Kolkata"):
    """'2025-08-18T12:30:00Z' -> 'YYYY-MM-DD HH:MM' in IST (or provided tz)."""
    tz = pytz.timezone(tz_name)
    # handle Z and +00:00
    dt_utc = datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
    return dt_utc.astimezone(tz).strftime("%Y-%m-%d %H:%M")
