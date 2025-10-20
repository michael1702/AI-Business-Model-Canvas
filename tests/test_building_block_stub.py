def test_prefill_building_block_stub(client, monkeypatch):
    # simula que tu función llm devuelve JSON válido para el bloque pedido
    def fake_llm(messages, **kwargs):
        return '{"value-propositions":"-Fresh\\n-Unique"}'
    # parchea llm en app.py
    monkeypatch.setattr("app.llm", fake_llm)

    r = client.post("/prefill_building_block", json={
        "product_idea": "bakery",
        "building_block": "value-propositions"
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data["value-propositions"].startswith("-Fresh")
