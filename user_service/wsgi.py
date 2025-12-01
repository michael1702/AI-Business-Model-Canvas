# user_service/wsgi.py
import os
from flask import Flask
from user_service.api import api

def create_app():
    app = Flask(__name__)
    # Basic config
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    app.config["JWT_EXP_S"] = int(os.getenv("JWT_EXP_S", "2592000"))
    
    app.register_blueprint(api)
    return app

app = create_app()