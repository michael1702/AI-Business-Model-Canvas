# group_service/wsgi.py
import os
from flask import Flask
from group_service.api import api

def create_app():
    app = Flask(__name__)
    # Basic config matching User Service for JWT validation
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    
    app.register_blueprint(api)
    return app

app = create_app()