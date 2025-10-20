import os
import pytest

from dotenv import load_dotenv

load_dotenv()  # zuerst versuchen, echte Werte zu laden
 
# Nur wenn wirklich nichts da ist (z. B. im CI ohne Secret), nimm Platzhalter:
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-test-placeholder"

#cliente de pruebas de Flask y helpers
@pytest.fixture
def client():
    #importar la app.py
    from app import app
    return app.test_client()