document.addEventListener('DOMContentLoaded', () => {
  ensureAuthUI();

  const out = document.getElementById('logout-btn');
  out?.addEventListener('click', () => {
    clearToken();
    sessionStorage.removeItem('currentBmc');
    location.href = '/';
  });

  const regEmail = document.getElementById('reg-email');
  const regPassword = document.getElementById('reg-password');
  const regBtn = document.getElementById('register-btn');
  const regMsg = document.getElementById('reg-msg');

  const loginEmail = document.getElementById('login-email');
  const loginPassword = document.getElementById('login-password');
  const loginBtn = document.getElementById('login-btn');
  const loginMsg = document.getElementById('login-msg');

  // --- REGISTER ---
  regBtn?.addEventListener('click', async () => {
    regMsg.textContent = 'Registering...';
    regMsg.style.color = 'black';
    try {
      const r = await fetch(API('/users/register'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: regEmail.value.trim(), password: regPassword.value })
      });

      // Debugging: Erst Text lesen
      const text = await r.text();
      console.log("Register Response Raw:", text);

      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        // Falls kein JSON zurückkam (z.B. HTML Fehlerseite vom Proxy)
        throw new Error(`Server Response not JSON: ${text.substring(0, 100)}...`);
      }

      if (r.ok) {
        regMsg.textContent = 'Registered! Please sign in.';
        regMsg.style.color = 'green';
      } else {
        regMsg.textContent = data.error || 'Registration failed';
        regMsg.style.color = 'red';
      }
    } catch (err) {
      console.error("Register Error:", err);
      regMsg.textContent = 'Error: ' + err.message;
      regMsg.style.color = 'red';
    }
  });

  // --- LOGIN ---
  loginBtn?.addEventListener('click', async () => {
    loginMsg.textContent = 'Signing in...';
    loginMsg.style.color = 'black';
    try {
      const r = await fetch(API('/users/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail.value.trim(), password: loginPassword.value })
      });

      // WICHTIG: Hier lesen wir erst den rohen Text, um zu sehen, was wirklich ankommt!
      const text = await r.text();
      console.log("Login Response Raw:", text);

      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        // Wenn das Parsen fehlschlägt, ist es meist eine HTML-Fehlerseite vom Proxy
        throw new Error("Server Error (Invalid JSON). Check Console.");
      }

      if (!r.ok) {
        loginMsg.textContent = data.error || 'Sign in failed';
        loginMsg.style.color = 'red';
        return;
      }

      // Prüfen, ob das Token wirklich da ist
      if (!data.access_token && !data.token) {
        console.error("Missing token in response:", data);
        throw new Error("No token received from server");
      }

      const token = data.access_token || data.token;
      setToken(token);
      
      loginMsg.textContent = 'Success!';
      loginMsg.style.color = 'green';
      
      // Kurze Verzögerung, damit man "Success" sieht
      setTimeout(() => {
        location.href = '/my-bmcs';
      }, 500);

    } catch (err) {
      console.error("Login Error Details:", err);
      // Zeige den echten Fehler an statt nur "Network error"
      loginMsg.textContent = 'Err: ' + err.message;
      loginMsg.style.color = 'red';
    }
  });
});