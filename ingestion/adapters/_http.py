import time
from typing import Any

import httpx

# Seconds to sleep after each request, to stay polite to the ATS host.
RATE_LIMIT_S = 0.5


def get_json(client: httpx.Client, url: str, params: dict[str, Any] | None = None) -> Any:
    """GET url and return parsed JSON; raises on non-2xx. Sleeps afterward to rate limit."""
    try:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    finally:
        time.sleep(RATE_LIMIT_S)
