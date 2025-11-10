document.addEventListener('DOMContentLoaded', async () => {
  ensureAuthUI();

  const token = getToken();
  if (!token) { location.href = '/auth'; return; }

  document.getElementById('logout-btn')?.addEventListener('click', () => {
    clearToken(); sessionStorage.removeItem('currentBmc'); location.href='/';
  });

  const list = document.getElementById('bmcs-list');
  const msg  = document.getElementById('bmcs-msg');
  const createBtn = document.getElementById('create-bmc');
  const newName   = document.getElementById('new-bmc-name');

  async function load() {
    list.innerHTML = 'Loading…'; msg.textContent = '';
    try {
      const r = await fetch(API('/users/me/bmcs'), { headers: { 'Authorization': `Bearer ${token}` }});
      if (r.status === 401) { clearToken(); location.href='/auth'; return; }
      const data = await r.json();
      if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = '<p>No BMCs yet. Create one above.</p>';
        return;
      }
      list.innerHTML = data.map(b => `
        <div class="bmc-row">
          <button class="button open-bmc" data-id="${b.id}" data-name="${b.name}">
            <strong>${b.name}</strong> <span class="muted">${b.updated || ''}</span>
          </button>
          <button class="button danger delete-bmc" data-id="${b.id}">Delete</button>
        </div>
      `).join('');

        // beim Öffnen:
        list.querySelectorAll('.open-bmc').forEach(btn => {
        btn.addEventListener('click', () => {
            const bmc = { id: btn.dataset.id, name: btn.dataset.name };
            sessionStorage.setItem('currentBmc', JSON.stringify(bmc));
            // Entferne ggf. alte Idee aus Session:
            sessionStorage.removeItem('product_idea');
            location.href = '/bmc';
        });
        });


      list.querySelectorAll('.delete-bmc').forEach(btn => {
        btn.addEventListener('click', async () => {
          if (!confirm('Delete this BMC?')) return;
          const id = btn.dataset.id;
          try {
            const r = await fetch(API(`/users/me/bmcs/${id}`), {
              method: 'DELETE',
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!r.ok) { msg.textContent = 'Delete failed'; return; }
            if (JSON.parse(sessionStorage.getItem('currentBmc') || 'null')?.id === id) {
              sessionStorage.removeItem('currentBmc');
            }
            load();
          } catch { msg.textContent = 'Network error'; }
        });
      });
    } catch {
      msg.textContent = 'Network error'; list.innerHTML = '';
    }
  }

  createBtn?.addEventListener('click', async () => {
    const name = (newName.value || '').trim() || 'Untitled';
    try {
      const r = await fetch(API('/users/me/bmcs'), {
        method:'POST',
        headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ name, data: {} })
      });
      if (!r.ok) { msg.textContent = 'Create failed'; return; }
      newName.value = '';
      load();
    } catch { msg.textContent = 'Network error'; }
  });

  load();
});
