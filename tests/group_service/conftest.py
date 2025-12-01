import pytest
from flask import Flask
import os

# Setze Umgebungsvariablen für den Test
os.environ["JWT_SECRET"] = "test-secret-key"

from group_service.api import api as group_api
from user_service.security import create_access_token

@pytest.fixture
def app():
    """Erstellt eine Instanz des Group-Services für Tests."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(group_api)
    return app

@pytest.fixture
def client(app):
    """Test-Client für Anfragen an die API."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Generiert Header für einen eingeloggten 'Owner'."""
    # Wir erstellen ein Token für eine fiktive User-ID
    token = create_access_token(user_id="owner-user-id", email="owner@test.com")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def other_user_headers():
    """Generiert Header für einen zweiten User."""
    token = create_access_token(user_id="other-user-id", email="other@test.com")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }