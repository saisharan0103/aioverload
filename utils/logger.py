import logging, sys
from datetime import datetime, timezone

class UtcFormatter(logging.Formatter):
    converter = lambda *args: datetime.now(timezone.utc).timetuple()

def get_logger(name="app"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(UtcFormatter("%(asctime)sZ %(levelname)s %(message)s"))
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    if not log.handlers:
        log.addHandler(handler)
    return log
