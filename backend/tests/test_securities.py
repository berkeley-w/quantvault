from fastapi.testclient import TestClient


def test_create_and_list_security(client: TestClient, auth_headers):
  resp = client.post(
    "/api/securities",
    json={
      "ticker": "AAPL",
      "name": "Apple Inc",
      "sector": "Technology",
      "price": 150.0,
      "shares_outstanding": 1000,
    },
    headers=auth_headers,
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["ticker"] == "AAPL"

  resp_list = client.get("/api/securities", headers=auth_headers)
  assert resp_list.status_code == 200
  rows = resp_list.json()
  tickers = [r["ticker"] for r in rows]
  assert "AAPL" in tickers


def test_update_security(client: TestClient, auth_headers):
  resp = client.post(
    "/api/securities",
    json={
      "ticker": "MSFT",
      "name": "Microsoft",
      "sector": "Technology",
      "price": 300.0,
      "shares_outstanding": 2000,
    },
    headers=auth_headers,
  )
  sec_id = resp.json()["id"]

  resp_upd = client.put(
    f"/api/securities/{sec_id}",
    json={"price": 310.0},
    headers=auth_headers,
  )
  assert resp_upd.status_code == 200
  assert resp_upd.json()["price"] == 310.0


def test_delete_security(client: TestClient, auth_headers):
  resp = client.post(
    "/api/securities",
    json={
      "ticker": "TSLA",
      "name": "Tesla",
      "sector": "Auto",
      "price": 200.0,
    },
    headers=auth_headers,
  )
  sec_id = resp.json()["id"]

  resp_del = client.delete(f"/api/securities/{sec_id}", headers=auth_headers)
  assert resp_del.status_code == 200

  resp_list = client.get("/api/securities", headers=auth_headers)
  tickers = [r["ticker"] for r in resp_list.json()]
  assert "TSLA" not in tickers


def test_create_security_unauthorized(client: TestClient):
  resp = client.post(
    "/api/securities",
    json={"ticker": "AAPL", "name": "Apple Inc", "price": 150.0},
  )
  assert resp.status_code in (401, 403)

