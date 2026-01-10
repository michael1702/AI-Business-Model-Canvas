import pytest
from flask import Flask
import os

# Setze Umgebungsvariablen für den Test
os.environ["JWT_SECRET"] = "test-secret-key"

from group_service.api import api as group_api
from user_service.security import create_access_token
from group_service.database import db 

@pytest.fixture
def app():
    """Erstellt eine Instanz des Group-Services für Tests."""
    app = Flask(__name__)
    
    # 1. Konfiguration für In-Memory-Datenbank hinzufügen
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # 2. Die Datenbank mit der Test-App verknüpfen
    db.init_app(app)

    app.register_blueprint(group_api)
    
    # 3. Tabellen im Application-Context anlegen
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Test-Client für Anfragen an die API."""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Generiert Header für einen eingeloggten 'Owner'."""
    # Token für fiktive User-ID
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