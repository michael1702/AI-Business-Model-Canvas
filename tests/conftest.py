import os
import pytest
import vcr
from service.config import create_app

from dotenv import load_dotenv

load_dotenv()  # load environment data
 
# VCR-Instance: specify how the vcr-cassette is being recorded
vcr_config = vcr.VCR(
    record_mode="once",  # first run recorded, afterwards it's reused to reduce the amount of calls for the API
    filter_headers=["authorization"], #hide the API key from the cassette
    decode_compressed_response=True, # prettier yaml format
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
)

#If no OPENAI-Key use sk-test-placeholder
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-test-placeholder"

#cliente de pruebas de Flask y helpers
@pytest.fixture
def client():
    app = create_app()
    return app.test_client()