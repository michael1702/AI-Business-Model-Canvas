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
  window.getCanvasData = getCanvasData;

  // If we have an existing BMC id, fetch from API and render
  async function loadExistingIfAny() {
      const path = window.location.pathname;
      let apiUrl;
      let bmcId;

      // 1. PRÜFUNG: Ist es ein Gruppen-BMC? 
      // URL Muster: /group/<group_id>/bmc/<bmc_id>
      const groupMatch = path.match(/\/group\/([^\/]+)\/bmc\/([^\/]+)/);

      if (groupMatch) {
          const groupId = groupMatch[1];
          bmcId = groupMatch[2];
          // WICHTIG: Wir nutzen den Gruppen-Endpunkt!
          apiUrl = API(`/groups/${groupId}/bmcs/${bmcId}`);
          console.log("Loading Group BMC:", bmcId);
      } else {
          // 2. FALLBACK: Normaler persönlicher BMC
          // Versucht ID aus URL zu lesen (z.B. /bmc/<id>) oder aus Session
          const urlId = path.split('/').pop();
          // Einfacher Check: Ist das letzte Element eine UUID? (grob geschätzt länge > 20)
          if (urlId.length > 20) {
              bmcId = urlId;
              apiUrl = API(`/users/me/bmcs/${bmcId}`); // oder Ihr entsprechender Endpunkt
          } else {
              // Kein BMC in URL -> vielleicht ein neuer oder aus Session (alte Logik)
              return; 
          }
      }

      if (!apiUrl) return;

      try {
          const r = await fetch(apiUrl, {
              headers: { 
                  'Authorization': `Bearer ${getToken()}`,
                  'Content-Type': 'application/json'
              }
          });

          if (r.status === 401) {
              console.warn("Unauthorized accessing BMC.");
              window.location.href = '/auth';
              return;
          }
          
          if (!r.ok) throw new Error("Failed to load BMC");

          const data = await r.json();
          
          // Titel setzen
          if (document.getElementById('product-idea')) {
              document.getElementById('product-idea').value = data.name || "";
          }
          
          // Daten in die Boxen füllen
          applyCanvasData(data.data || data); // Je nach Ihrer DB-Struktur (manchmal ist es data.data)

      } catch (e) {
          console.error("Error loading BMC:", e);
          // Optional: User benachrichtigen statt redirect
          alert("Could not load the Canvas. Do you have access?");
      }

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
