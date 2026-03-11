AGIFY_URL = "https://api.agify.io"


def make_result(name, status, latency_ms=None, details=""):
    return {
        "name": name,
        "status": status,
        "latency_ms": latency_ms,
        "details": details
    }


def test_status_code_200(client):
    result = client.get_json(AGIFY_URL, params={"name": "michael"})
    if result["ok"] and result["status_code"] == 200:
        return make_result("HTTP 200 sur nom valide", "PASS", result["latency_ms"])
    return make_result("HTTP 200 sur nom valide", "FAIL", result["latency_ms"], str(result))


def test_content_type_json(client):
    result = client.get_json(AGIFY_URL, params={"name": "michael"})
    content_type = result["headers"].get("Content-Type", "")
    if result["ok"] and "application/json" in content_type:
        return make_result("Content-Type JSON", "PASS", result["latency_ms"])
    return make_result("Content-Type JSON", "FAIL", result["latency_ms"], content_type)


def test_required_fields_present(client):
    result = client.get_json(AGIFY_URL, params={"name": "michael"})
    data = result["json"] or {}
    required = ["name", "age", "count"]
    missing = [field for field in required if field not in data]
    if result["ok"] and not missing:
        return make_result("Champs obligatoires présents", "PASS", result["latency_ms"])
    return make_result("Champs obligatoires présents", "FAIL", result["latency_ms"], f"Missing: {missing}")


def test_field_types(client):
    result = client.get_json(AGIFY_URL, params={"name": "michael"})
    data = result["json"] or {}

    valid_name = isinstance(data.get("name"), str) or data.get("name") is None
    valid_age = isinstance(data.get("age"), int) or data.get("age") is None
    valid_count = isinstance(data.get("count"), int)

    if result["ok"] and valid_name and valid_age and valid_count:
        return make_result("Types des champs", "PASS", result["latency_ms"])
    return make_result(
        "Types des champs",
        "FAIL",
        result["latency_ms"],
        f"Types invalides: name={type(data.get('name'))}, age={type(data.get('age'))}, count={type(data.get('count'))}"
    )


def test_empty_name_handled(client):
    result = client.get_json(AGIFY_URL, params={"name": ""})
    if result["ok"] and result["status_code"] == 200:
        return make_result("Gestion entrée vide", "PASS", result["latency_ms"])
    return make_result("Gestion entrée vide", "FAIL", result["latency_ms"], str(result))


def test_numeric_name_handled(client):
    result = client.get_json(AGIFY_URL, params={"name": "123"})
    if result["ok"] and result["status_code"] == 200:
        return make_result("Gestion entrée numérique", "PASS", result["latency_ms"])
    return make_result("Gestion entrée numérique", "FAIL", result["latency_ms"], str(result))


def test_latency_multiple_calls(client, n=5):
    latencies = []
    failures = 0

    for _ in range(n):
        result = client.get_json(AGIFY_URL, params={"name": "anya"})
        if result["ok"] and result["latency_ms"] is not None:
            latencies.append(result["latency_ms"])
        else:
            failures += 1

    if latencies:
        return make_result(
            f"Mesure de latence sur {n} appels",
            "PASS" if failures == 0 else "FAIL",
            round(sum(latencies) / len(latencies), 2),
            f"latencies={latencies}, failures={failures}"
        )

    return make_result(f"Mesure de latence sur {n} appels", "FAIL", None, "Aucune latence mesurée")


def get_all_tests():
    return [
        test_status_code_200,
        test_content_type_json,
        test_required_fields_present,
        test_field_types,
        test_empty_name_handled,
        test_numeric_name_handled,
        test_latency_multiple_calls,
    ]
