import os
from flask import Flask
from user_service.api import api
from user_service.database import db

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    app.config["JWT_EXP_S"] = int(os.getenv("JWT_EXP_S", "2592000"))
    
    # URL de conexión a PostgreSQL (leída de compose.yaml o render.yaml)
    # Formato: postgresql://user:pass@host:port/dbname
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local_users.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar DB
    db.init_app(app)
    
    # Crear tablas automáticamente (simple migration)
    with app.app_context():
        db.create_all()

    app.register_blueprint(api)
    return app

app = create_app()