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

    # 1. API Key Dummy setzen (für CI/CD wichtig)
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-test-placeholder"

    # 2. Den echten OpenAI Client laden
    # KORREKTUR: Das Argument 'model' entfernen
    app.config["LLM"] = OpenAIClient() 

    from bmc_service.api import api as bmc_api
    app.register_blueprint(bmc_api)

    return app

@pytest.fixture
def client(app):
    return app.test_client()