from fastapi.testclient import TestClient


def test_create_and_list_trader(client: TestClient, auth_headers):
  resp = client.post(
    "/api/traders",
    json={"name": "Alice", "desk": "EQ", "email": "alice@example.com"},
    headers=auth_headers,
  )
  assert resp.status_code == 200
  data = resp.json()
  assert data["name"] == "Alice"

  resp_list = client.get("/api/traders", headers=auth_headers)
  assert resp_list.status_code == 200
  names = [t["name"] for t in resp_list.json()]
  assert "Alice" in names


def test_update_trader(client: TestClient, auth_headers):
  resp = client.post(
    "/api/traders",
    json={"name": "Bob", "desk": "EQ", "email": "bob@example.com"},
    headers=auth_headers,
  )
  tid = resp.json()["id"]

  resp_upd = client.put(
    f"/api/traders/{tid}",
    json={"desk": "DERIV"},
    headers=auth_headers,
  )
  assert resp_upd.status_code == 200
  assert resp_upd.json()["desk"] == "DERIV"


def test_delete_trader(client: TestClient, auth_headers):
  resp = client.post(
    "/api/traders",
    json={"name": "Charlie", "desk": "EQ"},
    headers=auth_headers,
  )
  tid = resp.json()["id"]

  resp_del = client.delete(f"/api/traders/{tid}", headers=auth_headers)
  assert resp_del.status_code == 200

  resp_list = client.get("/api/traders", headers=auth_headers)
  names = [t["name"] for t in resp_list.json()]
  assert "Charlie" not in names


def test_traders_unauthorized(client: TestClient):
  resp = client.get("/api/traders")
  assert resp.status_code in (401, 403)

