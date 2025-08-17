import os, requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ApiError(Exception): pass

@retry(reraise=True,
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=1, max=8),
       retry=retry_if_exception_type((requests.RequestException, ApiError)))
def schedule_draft(api_key_env: str, content: str, schedule_date: str):
    url = "https://api.typefully.com/v1/drafts/"
    headers = {
        "X-API-KEY": f"Bearer {os.environ[api_key_env]}",
        "Content-Type": "application/json",
    }
    payload = {"content": content, "schedule-date": schedule_date}  # keep simple
    r = requests.post(url, json=payload, headers=headers, timeout=30)

    # Retry only on 5xx; surface 4xx details immediately
    if 500 <= r.status_code < 600:
        raise ApiError(f"Typefully 5xx: {r.status_code} {r.text[:300]}")
    if r.status_code >= 400:
        raise requests.HTTPError(f"{r.status_code} {r.text[:400]}", response=r)

    return r.json(), r.status_code
