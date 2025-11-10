# tests/test_users.py
from app import create_app
import pytest

@pytest.fixture
def client():
    return create_app().test_client()

def test_register_login_me_flow(client):
    r = client.post("/api/v1/users/register", json={"email":"a@b.com","password":"secret123"})
    assert r.status_code == 201

    r = client.post("/api/v1/users/login", json={"email":"a@b.com","password":"secret123"})
    assert r.status_code == 200
    token = r.get_json()["access_token"]

    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json()["email"] == "a@b.com"

    r = client.get("/api/v1/users/me/bmcs", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)
