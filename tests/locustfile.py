from locust import HttpUser, task, between

class BMCCanvasUser(HttpUser):
    # Wartezeit zwischen Aktionen (1-5 Sekunden)
    wait_time = between(1, 5)

    def on_start(self):
        """Wird ausgeführt, wenn ein 'User' startet: Registrieren (falls nötig) & Login"""
        self.email = "loadtest@example.com"
        self.password = "securepassword"
        self.token = None
        self.headers = {}

        # 1. Versuch: Einloggen
        response = self.client.post("/api/v1/users/login", json={
            "email": self.email, 
            "password": self.password
        })
        
        # 2. Wenn Login fehlschlägt (401), dann Registrieren
        if response.status_code == 401:
            self.client.post("/api/v1/users/register", json={
                "email": self.email, 
                "password": self.password
            })
            # 3. Nach Registrierung erneut einloggen
            response = self.client.post("/api/v1/users/login", json={
                "email": self.email, 
                "password": self.password
            })

        # Token speichern, wenn Login erfolgreich war
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed permanently: {response.status_code} - {response.text}")

    @task(3)
    def view_dashboard(self):
        # Nur ausführen, wenn wir eingeloggt sind
        if self.token:
            self.client.get("/api/v1/bmcs/", headers=self.headers)

    @task(1)
    def view_profile(self):
        if self.token:
            self.client.get("/api/v1/users/me", headers=self.headers)