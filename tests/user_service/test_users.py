import os
import pytest
from flask import Flask


os.environ.setdefault("JWT_SECRET", "test-super-secret")
os.environ.setdefault("JWT_EXP_S", "2592000")  # 30 days in seconds

@pytest.fixture(scope="session")
def app():
    # Build a minimal app for testing and register the Blueprint
    from user_service.api import api as user_api  # your Blueprint
    app = Flask(__name__)
    app.config.update(TESTING=True)
    app.register_blueprint(user_api)
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

# Helper: register + login and return token
@pytest.fixture()
def token(client):
    email = "alice@example.com"
    pwd   = "secret123"

    r = client.post("/api/v1/users/register", json={"email": email, "password": pwd})
    # Ok if already exists (from previous test run), otherwise 201
    assert r.status_code in (201, 400)

    r = client.post("/api/v1/users/login", json={"email": email, "password": pwd})
    assert r.status_code == 200
    data = r.get_json()
    return data["access_token"]

def test_register_and_login(client, token):
    # Test: Token should be a string
    assert isinstance(token, str)
    # Test: Access protected route (example)
    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["email"] == "alice@example.com"
