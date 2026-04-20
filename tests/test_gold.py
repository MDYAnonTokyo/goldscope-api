from fastapi.testclient import TestClient


def test_latest_gold_price_endpoint(client: TestClient) -> None:
    response = client.get("/gold/prices/latest")
    assert response.status_code == 200
    body = response.json()["item"]
    assert body["usd_oz"] > 0
    assert "price_date" in body


def test_gold_prices_range_query(client: TestClient) -> None:
    response = client.get(
        "/gold/prices",
        params={"start_date": "2024-01-01", "end_date": "2024-12-31", "limit": 0},
    )
    assert response.status_code == 200
    assert response.json()["count"] >= 12


def test_summary_and_returns_endpoints(client: TestClient) -> None:
    summary_response = client.get(
        "/gold/analytics/summary",
        params={"start_date": "2020-01-01", "end_date": "2025-12-31"},
    )
    assert summary_response.status_code == 200
    assert summary_response.json()["observation_count"] > 0

    returns_response = client.get("/gold/analytics/returns")
    assert returns_response.status_code == 200
    assert len(returns_response.json()["items"]) >= 2


def test_volatility_and_regime_endpoints(client: TestClient) -> None:
    volatility_response = client.get("/gold/analytics/volatility", params={"window_points": 12})
    assert volatility_response.status_code == 200
    assert volatility_response.json()["annualized_volatility"] >= 0

    regime_response = client.get("/gold/analytics/regime", params={"short_window": 3, "long_window": 6})
    assert regime_response.status_code == 200
    assert regime_response.json()["regime"] in {"bull", "bear", "sideways"}


def test_anomalies_and_drawdown_endpoints(client: TestClient) -> None:
    anomalies_response = client.get(
        "/gold/analytics/anomalies",
        params={"start_date": "2018-01-01", "end_date": "2025-12-31", "threshold": 1.5},
    )
    assert anomalies_response.status_code == 200
    assert anomalies_response.json()["count"] >= 0

    drawdown_response = client.get(
        "/gold/analytics/drawdown",
        params={"start_date": "2018-01-01", "end_date": "2025-12-31"},
    )
    assert drawdown_response.status_code == 200
    assert drawdown_response.json()["max_drawdown_pct"] <= 0


def test_invalid_query_returns_422(client: TestClient) -> None:
    response = client.get("/gold/analytics/volatility", params={"window_points": 1})
    assert response.status_code == 422


def test_empty_range_returns_404(client: TestClient) -> None:
    response = client.get(
        "/gold/analytics/summary",
        params={"start_date": "1800-01-01", "end_date": "1800-12-31"},
    )
    assert response.status_code == 404
