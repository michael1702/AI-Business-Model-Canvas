import json
from unittest.mock import patch, MagicMock

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

def test_add_member_inter_service(client, auth_headers):
    """
    Testet das Hinzufügen eines Mitglieds mit Mocking des HTTP-Calls.
    Wir simulieren die Antwort des User-Services.
    """
    # 1. Gruppe erstellen
    resp = client.post("/api/v1/groups/", json={"name": "Invite Team"}, headers=auth_headers)
    group_id = resp.get_json()["id"]

    # 2. Mocking vorbereiten
    # Wir 'patchen' das requests Modul dort, wo es verwendet wird (in group_service.api)
    with patch("group_service.api.requests.post") as mock_post:
        
        # SZENARIO: Der User-Service antwortet erfolgreich (200 OK)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "friend-user-id-123",
            "email": "friend@test.com"
        }
        mock_post.return_value = mock_response

        # 3. Request senden
        resp = client.post(f"/api/v1/groups/{group_id}/members", 
                           json={"email": "friend@test.com"}, 
                           headers=auth_headers)
        
        # 4. Assertions
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "added"
        assert data["user"]["id"] == "friend-user-id-123"
        
        # Sicherstellen, dass der Mock auch wirklich mit den richtigen Daten aufgerufen wurde
        mock_post.assert_called_once()
        # args[0] ist die URL. Prüfen, ob die URL den user-service enthält
        assert "users/lookup" in mock_post.call_args[0][0] 

def test_add_member_user_not_found(client, auth_headers):
    """Testet, wie der Group-Service reagiert, wenn der User-Service 404 liefert."""
    # 1. Gruppe erstellen
    resp = client.post("/api/v1/groups/", json={"name": "Empty Team"}, headers=auth_headers)
    group_id = resp.get_json()["id"]

    with patch("group_service.api.requests.post") as mock_post:
        # SZENARIO: User nicht gefunden
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "user_not_found"}
        mock_post.return_value = mock_response

        resp = client.post(f"/api/v1/groups/{group_id}/members", 
                           json={"email": "ghost@test.com"}, 
                           headers=auth_headers)
        
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "User not found or service error: user_not_found"

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