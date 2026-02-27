from fastapi.testclient import TestClient


def test_setup_creates_admin_and_allows_login(client: TestClient):
  resp = client.post(
    "/api/auth/setup",
    json={"username": "admin", "email": "admin@example.com", "password": "strongpass1"},
  )
  assert resp.status_code == 200
  data = resp.json()
  assert "access_token" in data
  assert data["user"]["role"] == "admin"

  resp_login = client.post(
    "/api/auth/login",
    json={"username": "admin", "password": "strongpass1"},
  )
  assert resp_login.status_code == 200
  assert "access_token" in resp_login.json()


def test_register_and_me_flow(client: TestClient):
  client.post(
    "/api/auth/setup",
    json={"username": "admin", "email": "admin@example.com", "password": "strongpass1"},
  )

  resp = client.post(
    "/api/auth/register",
    json={
      "username": "trader1",
      "email": "trader1@example.com",
      "password": "strongpass2",
    },
  )
  assert resp.status_code == 200
  token = resp.json()["access_token"]

  resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
  assert resp_me.status_code == 200
  body = resp_me.json()
  assert body["username"] == "trader1"
  assert body["email"] == "trader1@example.com"


def test_protected_requires_token(client: TestClient):
  resp = client.get("/api/securities")
  assert resp.status_code in (401, 403)

