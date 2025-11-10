document.addEventListener('DOMContentLoaded', async () => {
  ensureAuthUI();

  const token = getToken();
  if (!token) { location.href = '/auth'; return; }

  document.getElementById('logout-btn')?.addEventListener('click', () => {
    clearToken(); sessionStorage.removeItem('currentBmc'); location.href='/';
  });

  let current = JSON.parse(sessionStorage.getItem('currentBmc') || 'null'); // {id?, name}
  const ideaInput = document.getElementById('product-idea');

  // helpers
  const KEYS = [
    "key-partners","key-activities","key-resources",
    "value-propositions","customer-relationships","channels",
    "customer-segments","cost-structure","revenue-streams"
  ];

  function applyCanvasData(data) {
    KEYS.forEach(k => {
      const el = document.getElementById(`${k}-details`);
      if (el) el.value = (data && typeof data[k] === 'string') ? data[k] : "";
    });
  }

  function collectCanvas() {
    const data = {};
    KEYS.forEach(k => {
      const el = document.getElementById(`${k}-details`);
      data[k] = el ? el.value : "";
    });
    return data;
  }

  // If we have an existing BMC id, fetch from API and render
  async function loadExistingIfAny() {
    if (current?.id) {
      try {
        const r = await fetch(API(`/users/me/bmcs/${current.id}`), {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (r.ok) {
          const b = await r.json();
          if (ideaInput && !ideaInput.value) ideaInput.value = b.name || '';
          applyCanvasData(b.data || {});
          return true;
        }
      } catch { /* ignore */ }
    }
    return false;
  }

  // initial naming
  if (!current) {
    const name = (sessionStorage.getItem('product_idea') || ideaInput?.value || '').trim() || 'Untitled';
    current = { name };
    sessionStorage.setItem('currentBmc', JSON.stringify(current));
  }
  if (ideaInput && !ideaInput.value) ideaInput.value = current.name || '';

  // 1) Try to load existing saved canvas
  const loaded = await loadExistingIfAny();

  // 2) If none exists, optionally prefill once from example
  if (!loaded && ideaInput?.value) {
    const firstLoadKey = `prefilled_${current.id || 'new'}`;
    if (!sessionStorage.getItem(firstLoadKey)) {
      try {
        const resp = await fetch(API('/bmc/example'), {
          method: 'POST',
          headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ product_idea: ideaInput.value })
        });
        if (resp.ok) {
          const data = await resp.json();
          applyCanvasData(data);
          sessionStorage.setItem(firstLoadKey, '1');
        }
      } catch { /* ignore */ }
    }
  }

  const saveMsg = document.getElementById('save-msg');
  const saveBtn = document.getElementById('save-button');      // Update current
  const saveNewBtn = document.getElementById('save-new-button'); // Save as new (add this button in HTML)

  async function saveBmc(asNew = false) {
    saveMsg.textContent = 'Saving…';
    const name = (ideaInput?.value || '').trim() || 'Untitled';
    const payload = {
      id: asNew ? undefined : (current.id || undefined),
      name,
      data: collectCanvas()
    };
    try {
      const r = await fetch(API('/users/me/bmcs'), {
        method:'POST',
        headers: {
          'Content-Type':'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      const saved = await r.json();
      if (!r.ok) { saveMsg.textContent = saved.error || 'Save failed'; return; }
      current = { id: saved.id, name: saved.name };
      sessionStorage.setItem('currentBmc', JSON.stringify(current));
      sessionStorage.setItem('product_idea', saved.name);
      saveMsg.textContent = asNew ? 'Saved as new!' : 'Saved!';
    } catch {
      saveMsg.textContent = 'Network error';
    }
  }

  saveBtn?.addEventListener('click', () => saveBmc(false));
  saveNewBtn?.addEventListener('click', () => saveBmc(true));
});
