from fastapi.testclient import TestClient


def test_alerts_require_authentication(client: TestClient) -> None:
    response = client.get("/alerts")
    assert response.status_code == 401


def test_alert_crud_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/alerts",
        headers=auth_headers,
        json={
            "name": "Breakout Watch",
            "condition_type": "above",
            "threshold_value": 3200.0,
            "notes": "Watch for a breakout above resistance.",
            "active": True,
        },
    )
    assert create_response.status_code == 201
    alert_id = create_response.json()["id"]

    list_response = client.get("/alerts", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    detail_response = client.get(f"/alerts/{alert_id}", headers=auth_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["name"] == "Breakout Watch"

    update_response = client.patch(
        f"/alerts/{alert_id}",
        headers=auth_headers,
        json={"active": False, "threshold_value": 3300.0},
    )
    assert update_response.status_code == 200
    assert update_response.json()["active"] is False
    assert update_response.json()["threshold_value"] == 3300.0

    delete_response = client.delete(f"/alerts/{alert_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/alerts/{alert_id}", headers=auth_headers)
    assert missing_response.status_code == 404
