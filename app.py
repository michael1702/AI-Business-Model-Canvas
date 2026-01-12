import os, requests
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn= os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0, # Für Tests 100% aufzeichnen
    profiles_sample_rate=1.0,
)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env 
load_dotenv()

# --- NOTE: Blueprints and DB imports REMOVED. This is now just a UI Server. ---

def create_app():
    app = Flask(__name__, 
                static_folder="frontend/static", 
                template_folder="frontend/templates")

    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-prod")
    
    def build_service_url(env_var_name, default_host):
            host = os.getenv(env_var_name, default_host)
            
            # 1. Check: Ist es bereits eine volle URL (z.B. Public Render URL)?
            if host.startswith("http"):
                # Wenn am Ende ein Slash ist, weg damit
                return host.rstrip("/")
                
            # 2. Fallback: Es ist nur ein Hostname (z.B. "user-service" oder "localhost")
            # Dann bauen wir die interne URL mit Port 10000
            return f"http://{host}:10000"

    
    USER_SERVICE_URL = build_service_url("USER_SERVICE_HOST", "localhost")
    GROUP_SERVICE_URL = build_service_url("GROUP_SERVICE_HOST", "localhost")
    BMC_SERVICE_URL = build_service_url("BMC_SERVICE_HOST", "localhost")

# --- HELPER: Proxy Function ---
    def proxy_request(service_url, subpath):
            if subpath:
                url = f"{service_url}/{subpath}"
            else:
                url = service_url
                
            logger.info(f"Proxying request to: {url}")

            try:
                # 1. Header vorbereiten
                # Wir entfernen 'host' (macht requests automatisch)
                # WICHTIG: Wir entfernen 'accept-encoding' und setzen es auf 'identity'.
                # Das zwingt den Backend-Service, UNKOMPRIMIERTES JSON zu senden.
                req_headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'accept-encoding', 'content-length']}
                req_headers['Accept-Encoding'] = 'identity' 

                # 2. Request an den Backend-Service
                resp = requests.request(
                    method=request.method,
                    url=url,
                    headers=req_headers,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=True
                )

                # 3. Response Header filtern
                # Wir entfernen Encoding-Header, da wir jetzt sicher Plaintext haben
                excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
                headers = [(name, value) for (name, value) in resp.raw.headers.items()
                        if name.lower() not in excluded_headers]

                # 4. Antwort zurückgeben
                # resp.content sind jetzt sicher die rohen Bytes (Text), kein Gzip-Müll
                return Response(resp.content, resp.status_code, headers)

            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection failed to {url}: {e}")
                return jsonify({"error": f"Service unavailable at {url}"}), 503
            except Exception as e:
                logger.error(f"Unexpected error proxying to {url}: {e}")
                return jsonify({"error": "Internal Proxy Error"}), 500

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
    
    # 4. BMC Service / AI Helper Proxy
    # 4.1. Proxy for BMC Helper (z.B. /api/v1/bmc/example)
    @app.route('/api/v1/bmc/<path:subpath>', methods=['POST', 'GET'])
    def bmc_helper_proxy(subpath):
        # Leitet weiter an: http://bmc-service:5001/api/v1/bmc/example
        return proxy_request(BMC_SERVICE_URL, f"api/v1/bmc/{subpath}")

    # 4.2. Proxy for VPC Helper (z.B. /api/v1/vpc/tips)
    @app.route('/api/v1/vpc/<path:subpath>', methods=['POST', 'GET'])
    def vpc_helper_proxy(subpath):
        return proxy_request(BMC_SERVICE_URL, f"api/v1/vpc/{subpath}")

    # 4.3. Proxy for Chat (Exact Match)
    @app.route('/api/v1/chat_with_gpt5', methods=['POST'])
    def chat_gpt5_proxy():
        return proxy_request(BMC_SERVICE_URL, "api/v1/chat_with_gpt5")

    # --- ROUTES (UI ONLY) ---
    @app.route("/")
    def index(): 
        return render_template("index.html")
    
    @app.route("/testerror")
    def testError():
        1/0  # raises an error
        return "<p>Hello, World!</p>"
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

    @app.get("/group-bmcs/<group_id>")
    def group_bmcs(group_id): 
        return render_template("group-bmcs.html", group_id=group_id)


    @app.get('/group/<group_id>/bmc/<canvas_id>')
    def group_bmc_canvas(group_id, canvas_id): return render_template("bmc.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8888)), debug=True)