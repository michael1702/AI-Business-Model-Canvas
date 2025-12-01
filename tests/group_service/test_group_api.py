import json
from unittest.mock import patch

def test_create_group(client, auth_headers):
    """Testet das Erstellen einer neuen Gruppe."""
    payload = {"name": "My Startup Team"}
    resp = client.post("/api/v1/groups/", json=payload, headers=auth_headers)
    
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "My Startup Team"
    assert "id" in data
    assert data["owner_id"] == "owner-user-id"

def test_list_groups(client, auth_headers):
    """Testet, ob erstellte Gruppen in der Liste erscheinen."""
    # Erst eine Gruppe erstellen
    client.post("/api/v1/groups/", json={"name": "Group A"}, headers=auth_headers)
    
    # Dann Liste abrufen
    resp = client.get("/api/v1/groups/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    
    # Prüfen, ob mindestens eine Gruppe da ist
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(g["name"] == "Group A" for g in data)

def test_add_member_mocked(client, auth_headers):
    """
    Testet das Hinzufügen eines Mitglieds.
    Da wir keine echte DB haben, 'mocken' wir das UserRepo.
    """
    # 1. Gruppe erstellen
    resp = client.post("/api/v1/groups/", json={"name": "Invite Team"}, headers=auth_headers)
    group_id = resp.get_json()["id"]

    # 2. Mock für das User-Repository vorbereiten
    # Wir simulieren, dass '_user_repo.get_by_email' einen User zurückgibt
    with patch("group_service.api._user_repo") as mock_repo:
        # Das Objekt, das zurückgegeben wird, wenn wir nach Email suchen
        class MockUser:
            id = "invited-friend-id"
            email = "friend@test.com"
        
        mock_repo.get_by_email.return_value = MockUser()

        # 3. Request senden
        resp = client.post(f"/api/v1/groups/{group_id}/members", 
                           json={"email": "friend@test.com"}, 
                           headers=auth_headers)
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "member_added"
        # Gruppe sollte jetzt 2 Mitglieder haben (Owner + Friend)
        assert data["member_count"] == 2

def test_create_and_get_shared_bmc(client, auth_headers):
    """Testet CRUD für geteilte BMCs."""
    # 1. Gruppe erstellen
    g_resp = client.post("/api/v1/groups/", json={"name": "BMC Project"}, headers=auth_headers)
    group_id = g_resp.get_json()["id"]

    # 2. BMC in der Gruppe erstellen
    bmc_payload = {
        "name": "Shared Idea",
        "data": {"value-propositions": "Our great value"}
    }
    resp = client.post(f"/api/v1/groups/{group_id}/bmcs", json=bmc_payload, headers=auth_headers)
    assert resp.status_code == 200
    bmc_id = resp.get_json()["id"]

    # 3. BMC abrufen
    get_resp = client.get(f"/api/v1/groups/{group_id}/bmcs/{bmc_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data["name"] == "Shared Idea"
    assert data["data"]["value-propositions"] == "Our great value"