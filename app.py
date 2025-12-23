import os, requests
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

# Load .env 
load_dotenv()

# --- NOTE: Blueprints and DB imports REMOVED. This is now just a UI Server. ---

def create_app():
    app = Flask(__name__, 
                static_folder="frontend/static", 
                template_folder="frontend/templates")

    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    
    # Service URLs (Intern im Docker-Netzwerk erreichbar)
    BMC_SERVICE_URL = os.getenv("BMC_SERVICE_URL", "http://bmc-service:5001")
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:5002")
    GROUP_SERVICE_URL = os.getenv("GROUP_SERVICE_URL", "http://group-service:5003")

    # --- HELPER: Proxy Function ---
    def proxy_request(service_url, subpath):
        # Baut die Ziel-URL zusammen
        url = f"{service_url}/{subpath}"
        
        # Leitet die Anfrage mit derselben Methode, Headern und Body weiter
        try:
            resp = requests.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers if k.lower() != 'host'},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False
            )
            # Gibt die Antwort des Microservices an den Browser zurück
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in resp.raw.headers.items()
                       if name.lower() not in excluded_headers]
            return Response(resp.content, resp.status_code, headers)
        except requests.exceptions.ConnectionError:
            return jsonify({"error": "Service unavailable"}), 503

    # --- PROXY ROUTES ---
    # Diese Routen fangen die Anfragen vom Browser ab und leiten sie weiter

# --- PROXY ROUTES (Updated) ---
    
    # 1. BMC Service Proxy
    @app.route('/api/v1/bmcs', defaults={'subpath': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/api/v1/bmcs/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def bmc_proxy(subpath):
        return proxy_request(f"{BMC_SERVICE_URL}/api/v1/bmcs", subpath)

    # 2. User Service Proxy
    @app.route('/api/v1/users', defaults={'subpath': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/api/v1/users/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def user_proxy(subpath):
        return proxy_request(f"{USER_SERVICE_URL}/api/v1/users", subpath)

    # 3. Group Service Proxy
    @app.route('/api/v1/groups', defaults={'subpath': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/api/v1/groups/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def group_proxy(subpath):
        return proxy_request(f"{GROUP_SERVICE_URL}/api/v1/groups", subpath)

    # --- ROUTES (UI ONLY) ---
    @app.route("/")
    def index(): return render_template("index.html")

    @app.route("/auth")
    def auth(): return render_template("auth.html")

    @app.route("/profile")
    def profile(): return render_template("profile.html")

    @app.get("/my-bmcs")
    def my_bmcs(): return render_template("my-bmcs.html")

    @app.get("/bmc")
    def bmc(): return render_template("bmc.html")

    @app.get("/process")
    def process(): return render_template("process.html")
    
    @app.get("/key-partners")
    def key_partners(): return render_template("buildingblocks/key-partners.html")
    
    @app.get("/key-activities")
    def key_activities(): return render_template("buildingblocks/key-activities.html")
    
    @app.get("/key-resources")
    def key_resources(): return render_template("buildingblocks/key-resources.html")
    
    @app.get("/value-propositions")
    def value_proposition(): return render_template("buildingblocks/value-propositions.html")
    
    @app.get("/customer-segments")
    def customer_segments(): return render_template("buildingblocks/customer-segments.html")
    
    @app.get("/customer-relationships")
    def customer_relationships(): return render_template("buildingblocks/customer-relationships.html")
    
    @app.get("/channels")
    def channels(): return render_template("buildingblocks/channels.html")
    
    @app.get("/cost-structure")
    def cost_structure(): return render_template("buildingblocks/cost-structure.html")
    
    @app.get("/revenue-streams")
    def revenue_streams(): return render_template("buildingblocks/revenue-streams.html")
    
    @app.get("/value-proposition-canvas")
    def value_proposition_canvas(): return render_template("value-proposition-canvas.html")
    
    @app.get("/my-groups")
    def my_groups(): return render_template("my-groups.html")

    @app.get("/group/<group_id>/bmcs")
    def group_bmcs(group_id): return render_template("group-bmcs.html")


    @app.get('/group-bmcs/<canvas_id>')
    def group_bmc_canvas(canvas_id): return render_template("group-bmcs.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8888)), debug=True)