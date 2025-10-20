# tests/test_api_respx.py
import respx
from httpx import Response
from tests.helpers_openai import make_openai_responses_json

@respx.mock
def test_example_canvas_respx(client):
    mocked_json = make_openai_responses_json({
        "value-propositions": "-Fresh\n-Quality ingredients",
        "customer-segments": "-Local residents",
    })

    # Mocke den Responses-Endpoint
    respx.post("https://api.openai.com/v1/responses").mock(
        return_value=Response(200, json=mocked_json)
    )

    r = client.post("/example_canvas_by_product", json={"product_idea": "bakery"})
    assert r.status_code == 200, r.data
    data = r.get_json()
    assert "value-propositions" in data
    assert data["value-propositions"].startswith("-Fresh")
