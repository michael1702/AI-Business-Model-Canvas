import os
import pytest
from flask import Flask
from user_service.api import api as user_api
from user_service.database import db 

os.environ.setdefault("JWT_SECRET", "test-super-secret")
os.environ.setdefault("JWT_EXP_S", "2592000")

@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    
    # 1. Configure the DB for testing (In-memory SQLite is fast and isolated)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # 2. Initialize the extension with the test app
    # This fixes the "Flask app is not registered..." error
    db.init_app(app)

    app.register_blueprint(user_api)
    
    # 3. Create tables so the tests have a schema to work with
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def token(client):
    email = "alice@example.com"
    pwd   = "secret123"

    r = client.post("/api/v1/users/register", json={"email": email, "password": pwd})
    assert r.status_code in (201, 400)

    r = client.post("/api/v1/users/login", json={"email": email, "password": pwd})
    assert r.status_code == 200
    data = r.get_json()
    return data["access_token"]