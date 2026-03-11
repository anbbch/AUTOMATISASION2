from datetime import datetime, timezone
from statistics import mean

from tester.client import HttpClient
from tester.tests import get_all_tests


def percentile_95(values):
    if not values:
        return 0
    values = sorted(values)
    index = int(0.95 * (len(values) - 1))
    return values[index]


def run_all_tests():
    client = HttpClient(timeout=3, max_retries=1)
    tests = get_all_tests()
    results = []

    for test_func in tests:
        try:
            results.append(test_func(client))
        except Exception as e:
            results.append({
                "name": test_func.__name__,
                "status": "FAIL",
                "latency_ms": None,
                "details": f"Unhandled exception: {str(e)}"
            })

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    latencies = [r["latency_ms"] for r in results if isinstance(r["latency_ms"], (int, float))]
    total = len(results)

    summary = {
        "passed": passed,
        "failed": failed,
        "error_rate": round(failed / total, 3) if total else 0,
        "latency_ms_avg": round(mean(latencies), 2) if latencies else 0,
        "latency_ms_p95": round(percentile_95(latencies), 2) if latencies else 0,
        "availability": round((passed / total) * 100, 2) if total else 0
    }

    return {
        "api": "Agify",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "tests": results
    }
