import json
from tests.bmc_service.conftest import vcr_config

CASSETTE_PATH = "tests/cassettes/example_canvas.yaml"

def test_example_canvas_vcr(client):
    with vcr_config.use_cassette(CASSETTE_PATH) as cass:
        r = client.post("/api/v1/bmc/example", json={"product_idea": "bakery"})

        # Response-Checks
        assert r.status_code == 200
        data = r.get_json()
        assert "value-propositions" in data
        assert isinstance(data["value-propositions"], str)
        assert len(data["value-propositions"]) > 0

        # Request-Checks: exactly one API-call
        assert len(cass.requests) == 1
        req = cass.requests[0]

        assert req.method == "POST"
        assert req.uri == "https://api.openai.com/v1/responses"

        raw = req.body.decode("utf-8") if isinstance(req.body, bytes) else req.body
        body = json.loads(raw)

        # Model and limits like in the cassette
        assert body["model"].startswith("gpt-5-mini")
        assert body["max_output_tokens"] == 2000  

        # Prompt-Form: input is List with user-Content and contains "bakery"
        assert isinstance(body["input"], list) and body["input"]
        first = body["input"][0]
        assert first.get("role") == "user"
        content = first.get("content", "")
        assert "building blocks" in content.lower()
        assert "bakery" in content.lower()
