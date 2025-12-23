# app.py (project root)
import os
from flask import Flask, render_template
from dotenv import load_dotenv
from bmc_service.adapters.openai_client import OpenAIClient
from bmc_service.app_logging import setup_logging

# Load .env (For JWT_SECRET and Service URLs)
load_dotenv()

def create_app():
    app = Flask(__name__, 
                static_folder="frontend/static", 
                template_folder="frontend/templates")

    # --- CONFIGURATION ---
    # We no longer need SQLALCHEMY_DATABASE_URI here!
    # The frontend doesn't talk to the DB directly anymore.
    
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    
    # Pass Service URLs to templates if needed (so JS knows where to fetch data)
    @app.context_processor
    def inject_service_urls():
        return dict(
            bmc_service_url=os.getenv("BMC_SERVICE_URL", "http://localhost:5001"),
            user_service_url=os.getenv("USER_SERVICE_URL", "http://localhost:5002"),
            group_service_url=os.getenv("GROUP_SERVICE_URL", "http://localhost:5003")
        )

    app.config["LLM"] = OpenAIClient()   # <- Service injection
    setup_logging(app)                   # <- Enable centralized logging

    # --- ROUTES (UI ONLY) ---
    # These routes just serve the HTML "Shells". 
    # The JavaScript in these pages will fetch data from the URLs above.

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    @app.route("/register")
    def auth():
        # Ensure your auth.js posts to user_service_url
        return render_template("auth.html")

    @app.route("/profile")
    def profile():
        return render_template("profile.html")

    @app.get("/my-bmcs")
    def my_bmcs():
        return render_template("my-bmcs.html")

    @app.get("/bmc/<canvas_id>")
    def bmc_canvas(canvas_id):
        # The JS will use the canvas_id to fetch details from BMC Service
        return render_template("bmc.html", canvas_id=canvas_id)

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
