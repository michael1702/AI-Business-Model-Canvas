import os
import pytest
import vcr
from flask import Flask
from dotenv import load_dotenv

# WICHTIG: Importiere den Blueprint des Services und den Adapter direkt
from bmc_service.api import api as bmc_api
from bmc_service.adapters.openai_client import OpenAIClient 

load_dotenv()

# VCR Config (bleibt wie es war)
vcr_config = vcr.VCR(
    record_mode="once", 
    filter_headers=["authorization"],
    decode_compressed_response=True,
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
)

@pytest.fixture
def app():
    """
    Erstellt eine isolierte Instanz NUR des BMC-Services.
    Kein Frontend-Proxy dazwischen!
    """
    app = Flask(__name__)
    app.config["TESTING"] = True

    # 1. API Key Dummy setzen, falls nicht vorhanden (für CI/CD wichtig)
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-test-placeholder"

    # 2. Den echten OpenAI Client laden (damit VCR ihn aufzeichnen kann)
    # Wir hängen ihn an die App-Config, da api.py darauf zugreift: current_app.config["LLM"]
    app.config["LLM"] = OpenAIClient(model="gpt-5-mini")

    # 3. Den Blueprint registrieren
    app.register_blueprint(bmc_api)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()