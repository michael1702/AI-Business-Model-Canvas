from flask import Flask
from bmc_service.api import api 
from bmc_service.adapters.openai_client import OpenAIClient
from bmc_service.app_logging import setup_logging

def create_app():
    app = Flask(__name__,
            static_folder="static",
            template_folder="templates")
    app.register_blueprint(api)          # <- /api/v1/...
    app.config["LLM"] = OpenAIClient()   # <- Service-Injektion
    setup_logging(app)                   # <- Logging zentral aktivieren
    return app