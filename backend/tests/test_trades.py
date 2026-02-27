from fastapi.testclient import TestClient


def seed_security_and_trader(client: TestClient, auth_headers):
  client.post(
    "/api/securities",
    json={"ticker": "AAPL", "name": "Apple", "price": 150.0},
    headers=auth_headers,
  )
  client.post(
    "/api/traders",
    json={"name": "Alice", "desk": "EQ"},
    headers=auth_headers,
  )


def test_create_trade_and_holdings(client: TestClient, auth_headers):
  seed_security_and_trader(client, auth_headers)

  resp = client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "BUY",
      "quantity": 10,
      "price": 150.0,
      "trader_name": "Alice",
    },
    headers=auth_headers,
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["ticker"] == "AAPL"

  resp_holdings = client.get("/api/holdings", headers=auth_headers)
  assert resp_holdings.status_code == 200
  holdings = resp_holdings.json()
  assert holdings[0]["ticker"] == "AAPL"
  assert holdings[0]["net_quantity"] == 10


def test_reject_and_reinstate_trade(client: TestClient, auth_headers):
  seed_security_and_trader(client, auth_headers)
  resp = client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "BUY",
      "quantity": 5,
      "price": 150.0,
      "trader_name": "Alice",
    },
    headers=auth_headers,
  )
  tid = resp.json()["id"]

  resp_reject = client.post(
    f"/api/trades/{tid}/reject",
    json={"rejection_reason": "Test reason"},
    headers=auth_headers,
  )
  assert resp_reject.status_code == 200
  assert resp_reject.json()["status"] == "REJECTED"

  resp_reinstate = client.post(
    f"/api/trades/{tid}/reinstate",
    headers=auth_headers,
  )
  assert resp_reinstate.status_code == 200
  assert resp_reinstate.json()["status"] == "ACTIVE"


def test_restricted_list_blocks_trade(client: TestClient, auth_headers):
  client.post(
    "/api/securities",
    json={"ticker": "TSLA", "name": "Tesla", "price": 200.0},
    headers=auth_headers,
  )
  client.post(
    "/api/traders",
    json={"name": "Risky", "desk": "EQ"},
    headers=auth_headers,
  )
  client.post(
    "/api/restricted",
    json={"ticker": "TSLA"},
    headers=auth_headers,
  )

  resp = client.post(
    "/api/trades",
    json={
      "ticker": "TSLA",
      "side": "BUY",
      "quantity": 1,
      "price": 200.0,
      "trader_name": "Risky",
    },
    headers=auth_headers,
  )
  assert resp.status_code == 400
  assert "restricted list" in resp.json()["detail"]


def test_create_trade_unauthorized(client: TestClient):
  resp = client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "BUY",
      "quantity": 1,
      "price": 150.0,
      "trader_name": "Alice",
    },
  )
  assert resp.status_code in (401, 403)

