import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import Base


TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
  db = TestSessionLocal()
  try:
    yield db
  finally:
    db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
  Base.metadata.create_all(bind=engine)
  try:
    yield
  finally:
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
  with TestClient(app) as c:
    yield c


@pytest.fixture
def auth_headers(client):
  resp = client.post(
    "/api/auth/setup",
    json={
      "username": "testadmin",
      "email": "admin@test.com",
      "password": "testpass123",
    },
  )
  assert resp.status_code == 200
  token = resp.json()["access_token"]
  return {"Authorization": f"Bearer {token}"}

