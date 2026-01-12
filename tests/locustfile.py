import random
import string
from locust import HttpUser, task, between

def random_string(length=8):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

class BMCCanvasUser(HttpUser):
    # WICHTIG: Erhöhe die Wartezeit drastisch (10-30 Sekunden), 
    # um wie ein echter Mensch zu wirken und Rate-Limits zu vermeiden.
    wait_time = between(10, 30)

    def on_start(self):
        self.email = f"user_{random_string()}@test.com"
        self.password = "secure123"
        self.token = None
        
        # WICHTIG: Setze einen realistischen Browser User-Agent!
        # Cloudflare prüft diesen Header sehr genau.
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://aibmc-frontend.onrender.com",
            "Referer": "https://aibmc-frontend.onrender.com/auth"
        }

        # 1. Registrieren
        self.client.post("/api/v1/users/register", json={
            "email": self.email,
            "password": self.password
        }, headers=self.headers)

        # 2. Login
        response = self.client.post("/api/v1/users/login", json={
            "email": self.email,
            "password": self.password
        }, headers=self.headers)

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            # Authorization Header für folgende Requests setzen
            self.headers["Authorization"] = f"Bearer {self.token}"
        elif response.status_code == 429:
            print("⚠️ Still getting 429 (Rate Limited) from Cloudflare!")
        else:
            print(f"Login failed: {response.status_code}")

    @task(1)
    def view_profile(self):
        if self.token:
            self.client.get("/api/v1/users/me", headers=self.headers)