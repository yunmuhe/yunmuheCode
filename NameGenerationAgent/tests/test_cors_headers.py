import src.web.app as web_app_module


def test_health_endpoint_returns_cors_headers():
    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get(
            "/health",
            headers={"Origin": "http://127.0.0.1:4174"},
        )

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:4174"


def test_generate_options_preflight_returns_cors_headers():
    app = web_app_module.app
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.open(
            "/generate",
            method="OPTIONS",
            headers={
                "Origin": "http://127.0.0.1:4174",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:4174"
    assert "POST" in (response.headers.get("Access-Control-Allow-Methods") or "")
    allow_headers = (response.headers.get("Access-Control-Allow-Headers") or "").lower()
    assert "content-type" in allow_headers
    assert "authorization" in allow_headers
