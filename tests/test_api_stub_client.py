# tests/test_api_stub_client.py
import json

def test_example_canvas_stub_client(client, monkeypatch):
    class DummyResp:
        def __init__(self, text):
            self.output_text = text

    def fake_create(*args, **kwargs):
        # Das ist genau der Text, den deine Route später parsed
        payload = {
            "value-propositions": "-Fresh\n-Quality ingredients",
            "customer-segments": "-Local residents",
        }
        return DummyResp(json.dumps(payload))

    monkeypatch.setattr("app.client.responses.create", fake_create)

    r = client.post("/example_canvas_by_product", json={"product_idea": "bakery"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["value-propositions"].startswith("-Fresh")
