document.addEventListener('DOMContentLoaded', () => {
  ensureAuthUI();
  const out = document.getElementById('logout-btn');
  out?.addEventListener('click', () => { clearToken(); sessionStorage.removeItem('currentBmc'); location.href='/'; });

  const regEmail = document.getElementById('reg-email');
  const regPassword = document.getElementById('reg-password');
  const regBtn = document.getElementById('register-btn');
  const regMsg = document.getElementById('reg-msg');

  const loginEmail = document.getElementById('login-email');
  const loginPassword = document.getElementById('login-password');
  const loginBtn = document.getElementById('login-btn');
  const loginMsg = document.getElementById('login-msg');

  regBtn?.addEventListener('click', async () => {
    regMsg.textContent = 'Registering…';
    try {
      const r = await fetch(API('/users/register'), {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email: regEmail.value.trim(), password: regPassword.value })
      });
      const data = await r.json();
      regMsg.textContent = r.ok ? 'Registered. Please sign in.' : (data.error || 'Registration failed');
    } catch { regMsg.textContent = 'Network error'; }
  });

  loginBtn?.addEventListener('click', async () => {
    loginMsg.textContent = 'Signing in…';
    try {
      const r = await fetch(API('/users/login'), {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email: loginEmail.value.trim(), password: loginPassword.value })
      });
      const data = await r.json();
      if (!r.ok) { loginMsg.textContent = data.error || 'Sign in failed'; return; }
      setToken(data.access_token);
      loginMsg.textContent = 'Success!';
      location.href = '/my-bmcs';
    } catch { loginMsg.textContent = 'Network error'; }
  });
});
