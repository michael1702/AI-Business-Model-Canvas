from tests.bmc_service.conftest import vcr_config as vcr
import json


CASSETTE_PATH = "tests/cassettes/prefill_building_block.yaml"


def test_prefill_building_block_vcr(client):
    # Context Manager: Zugriff auf die Requests in der Kassette
    with vcr.use_cassette(CASSETTE_PATH) as cass:
        resp = client.post(
            "/api/v1/bmc/prefill_building_block",
            json={"product_idea": "bakery", "building_block": "value-propositions"},
        )

        # --- Response-Prüfungen ---
        assert resp.status_code == 200
        data = resp.get_json()
        assert "value-propositions" in data
        assert isinstance(data["value-propositions"], str)
        assert len(data["value-propositions"]) > 0
        # Request-Check to openai
        # There should only be exactly ONE external request
        assert len(cass.requests) == 1
        req = cass.requests[0]
        # Methode & Endpoint
        assert req.method == "POST"
        assert req.uri == "https://api.openai.com/v1/responses"

        # Check body (model, tokens, input-Shape)
        raw = req.body
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        body = json.loads(raw)

        # configuration of what I send matches the goal
        assert body["model"].startswith("gpt-5-mini")  # model
        assert body["max_output_tokens"] == 1000 #max token

        assert isinstance(body["input"], list) and body["input"], "input should be a list and not empty"
        first = body["input"][0]
        assert first.get("role") == "user"
        content = first.get("content", "")
        assert "building block" in content.lower()
        assert "bakery" in content.lower()   # Product-Idea is sent successfully