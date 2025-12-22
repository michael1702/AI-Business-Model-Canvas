# app.py (project root)
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from bmc_service.adapters.openai_client import OpenAIClient
from bmc_service.app_logging import setup_logging

# Load .env (JWT_SECRET etc.)
load_dotenv()

# Import blueprints
from bmc_service.api import api as bmc_api
from user_service.api import api as user_api
from group_service.api import api as group_api

# Import database object
from user_service.database import db


def create_app():
    app = Flask(__name__, 
                static_folder="frontend/static", 
                template_folder="frontend/templates")

    # Load configuration

    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    app.config["JWT_EXP_S"] = int(os.getenv("JWT_EXP_S", "2592000"))
    
    # Database URL
    default_db = "postgresql://admin:secret@db:5432/aibmc_db"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialization:  One instance for all the app
    db.init_app(app)

    # Create tables (in monolith mode, the frontend does this)
    with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                print(f"Warning creating tables: {e}")


    # Register blueprints
    app.register_blueprint(user_api)
    app.register_blueprint(group_api)
    app.register_blueprint(bmc_api)
    app.config["LLM"] = OpenAIClient()   # <- Service injection
    setup_logging(app)                   # <- Enable centralized logging

    # HTML pages 
    @app.get("/")
    def index():
        return render_template("index.html")
    
    @app.get("/auth")
    def auth(): return render_template("auth.html")

    @app.get("/my-bmcs")
    def my_bmcs(): return render_template("my-bmcs.html")

    @app.get("/bmc")
    def bmc(): return render_template("bmc.html")

    @app.get("/profile")
    def profile(): return render_template("profile.html")

    @app.get("/process")
    def process():
        return render_template("process.html")

    @app.get("/key-partners")
    def key_partners():
        return render_template("buildingblocks/key-partners.html")

    @app.get("/key-activities")
    def key_activities():
        return render_template("buildingblocks/key-activities.html")

    @app.get("/key-resources")
    def key_resources():
        return render_template("buildingblocks/key-resources.html")

    @app.get("/value-propositions")
    def value_proposition():
        return render_template("buildingblocks/value-propositions.html")

    @app.get("/customer-segments")
    def customer_segments():
        return render_template("buildingblocks/customer-segments.html")

    @app.get("/customer-relationships")
    def customer_relationships():
        return render_template("buildingblocks/customer-relationships.html")

    @app.get("/channels")
    def channels():
        return render_template("buildingblocks/channels.html")

    @app.get("/cost-structure")
    def cost_structure():
        return render_template("buildingblocks/cost-structure.html")

    @app.get("/revenue-streams")
    def revenue_streams():
        return render_template("buildingblocks/revenue-streams.html")

    @app.get("/value-proposition-canvas")
    def value_proposition_canvas():
        return render_template("value-proposition-canvas.html")
    
    @app.get("/my-groups")
    def my_groups(): 
        return render_template("my-groups.html")

    @app.get("/group/<group_id>/bmcs")
    def group_bmcs(group_id): 
        return render_template("group-bmcs.html")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8888)), debug=True)
