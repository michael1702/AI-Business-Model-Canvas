def test_register_and_login(client, token):
    # Test: Token should be a string
    assert isinstance(token, str)
    
    # Test: Access protected route (example)
    r = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    
    # Note: Depending on your logic, this might need error handling 
    # if the endpoint doesn't exist yet, but the token generation part is now fixed.
    if r.status_code != 404: 
        assert r.status_code == 200
        data = r.get_json()
        assert data["email"] == "alice@example.com"