import vcr

@vcr.use_cassette(
    "tests/cassettes/example_canvas.yaml",
    record_mode="once",
    filter_headers=["authorization"],          # Key maskieren
    decode_compressed_response=True            # hübschere YAML
)
def test_example_canvas_vcr(client):
    r = client.post("/example_canvas_by_product", json={"product_idea": "bakery"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["value-propositions"].startswith("-Fresh")