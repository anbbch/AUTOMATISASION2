import time
import requests


class HttpClient:
    def __init__(self, timeout=3, max_retries=1):
        self.timeout = timeout
        self.max_retries = max_retries

    def get_json(self, url, params=None):
        attempts = 0
        last_error = None

        while attempts <= self.max_retries:
            attempts += 1
            start = time.perf_counter()

            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if response.status_code == 429 and attempts <= self.max_retries:
                    time.sleep(1)
                    continue

                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "json": response.json() if "application/json" in response.headers.get("Content-Type", "") else None,
                    "latency_ms": latency_ms,
                    "error": None
                }

            except requests.exceptions.Timeout as e:
                last_error = f"Timeout: {str(e)}"
                if attempts <= self.max_retries:
                    time.sleep(0.5)
                    continue

            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"
                break

            except ValueError as e:
                last_error = f"Invalid JSON: {str(e)}"
                break

        return {
            "ok": False,
            "status_code": None,
            "headers": {},
            "json": None,
            "latency_ms": None,
            "error": last_error
        }
