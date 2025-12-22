import os
from flask import Flask
from group_service.api import api
from group_service.database import db

def create_app():
    app = Flask(__name__)
    
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "secret")
    # Same DB URL as in User Service
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///groups.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    app.register_blueprint(api)
    return app

app = create_app()