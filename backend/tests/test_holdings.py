from fastapi.testclient import TestClient


def test_holdings_computation_multiple_trades(client: TestClient, auth_headers):
  client.post(
    "/api/securities",
    json={"ticker": "AAPL", "name": "Apple", "price": 100.0},
    headers=auth_headers,
  )
  client.post(
    "/api/traders",
    json={"name": "Alice", "desk": "EQ"},
    headers=auth_headers,
  )

  client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "BUY",
      "quantity": 10,
      "price": 100.0,
      "trader_name": "Alice",
    },
    headers=auth_headers,
  )
  client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "BUY",
      "quantity": 5,
      "price": 110.0,
      "trader_name": "Alice",
    },
    headers=auth_headers,
  )
  client.post(
    "/api/trades",
    json={
      "ticker": "AAPL",
      "side": "SELL",
      "quantity": 3,
      "price": 120.0,
      "trader_name": "Alice",
    },
    headers=auth_headers,
  )

  resp = client.get("/api/holdings", headers=auth_headers)
  assert resp.status_code == 200
  holdings = resp.json()
  assert len(holdings) == 1
  h = holdings[0]
  assert h["ticker"] == "AAPL"
  assert h["net_quantity"] == 12

