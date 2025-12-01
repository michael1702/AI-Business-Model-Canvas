// frontend/static/scripts/groups.js
document.addEventListener('DOMContentLoaded', async () => {
  ensureAuthUI();

  const token = getToken();
  if (!token) { location.href = '/auth'; return; }
  
  const path = window.location.pathname.replace(/\/+$/, "");
  
  // Logic for the Group Detail / Editor Page
  if (path.includes('/group/') && path.endsWith('/bmcs')) {
    const urlParts = path.split('/');
    const validParts = urlParts.filter(p => p); 
    const groupId = validParts[1]; 
    const bmcId = new URLSearchParams(window.location.search).get('bmc_id');
    
    // Load Group Info & Members (Always done to get group name)
    await loadGroupInfoAndMembers(groupId);

    if (bmcId) {
        // Show Editor
        document.getElementById('group-overview-section').style.display = 'none';
        document.getElementById('group-bmc-editor').style.display = 'block';
        await setupGroupBmcEditor(groupId, bmcId);
        
        // Initialize AI Buttons (re-using logic from index.js if available, or redefining)
        setupAiButtons(); 
    } else {
        // Show List
        document.getElementById('group-bmc-editor').style.display = 'none';
        document.getElementById('group-overview-section').style.display = 'block';
        await loadGroupBmcs(groupId);
    }
  } 
  // Logic for the Group Overview Page
  else if (path === '/my-groups') {
    await loadMyGroups();
  }
});

// --- Group List Logic ---
async function loadMyGroups() {
    const list = document.getElementById('groups-list');
    const msg  = document.getElementById('groups-msg');
    const createBtn = document.getElementById('create-group');
    const newName   = document.getElementById('new-group-name');
    const token = getToken();

    // Attach event listener only once
    createBtn.onclick = async () => {
        const name = (newName.value || '').trim();
        if (!name) { msg.textContent = 'Give a name!'; return; }
        msg.textContent = 'Creating…';
        try {
            const r = await fetch(API('/groups/'), {
                method:'POST',
                headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ name })
            });
            const data = await r.json();
            if (!r.ok) { msg.textContent = data.error || 'Create failed'; return; }
            newName.value = '';
            await loadMyGroups(); // Reload list
        } catch { msg.textContent = 'Network error.'; }
    };

    list.innerHTML = 'Loading…'; msg.textContent = '';
    try {
      const r = await fetch(API('/groups/'), { headers: { 'Authorization': `Bearer ${token}` }});
      if (r.status === 401) { clearToken(); location.href='/auth'; return; }
      const data = await r.json();

      if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = '<p>No groups yet. Create one above.</p>';
        return;
      }
      
      list.innerHTML = data.map(g => `
        <div class="group-row" style="margin-bottom:10px; padding:10px; background:white; border:1px solid #ddd; border-radius:5px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <strong>${g.name}</strong> <span class="muted" style="font-size:0.9em; color:#666;">(${g.is_owner ? 'Owner' : 'Member'}, ${g.member_count} members)</span>
          </div>
          <button class="button open-group" data-id="${g.id}">Open</button>
        </div>
      `).join('');

      list.querySelectorAll('.open-group').forEach(btn => {
        btn.addEventListener('click', () => {
            location.href = `/group/${btn.dataset.id}/bmcs`;
        });
      });
    } catch { msg.textContent = 'Network error loading groups.'; list.innerHTML = ''; }
}

// --- Group Detail Logic ---

async function loadGroupInfoAndMembers(groupId) {
    const token = getToken();
    const groupNameHeader = document.getElementById('group-name-header');
    const membersList = document.getElementById('members-list');
    const inviteBtn = document.getElementById('invite-member-btn');
    const inviteInput = document.getElementById('invite-email');
    const inviteMsg = document.getElementById('invite-msg');

    try {
        const r = await fetch(API(`/groups/${groupId}`), { headers: { 'Authorization': `Bearer ${token}` }});
        if (!r.ok) return;
        const group = await r.json();
        
        if(groupNameHeader) groupNameHeader.textContent = `Group: ${group.name}`;
        
        // Render Members
        if(membersList && group.members) {
            membersList.innerHTML = group.members.map(m => `
                <li style="padding: 5px 0; border-bottom: 1px solid #eee;">
                    ${m.email} ${m.is_owner ? '👑' : ''}
                </li>
            `).join('');
        }

        // Invite Logic
        if(inviteBtn) {
            inviteBtn.onclick = async () => {
                const email = inviteInput.value.trim();
                if(!email) return;
                inviteMsg.textContent = "Inviting...";
                try {
                    const rInv = await fetch(API(`/groups/${groupId}/members`), {
                        method: 'POST',
                        headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
                        body: JSON.stringify({ email: email })
                    });
                    const res = await rInv.json();
                    if(rInv.ok) {
                        inviteMsg.textContent = "User added!";
                        inviteInput.value = "";
                        await loadGroupInfoAndMembers(groupId); // Refresh list
                    } else {
                        inviteMsg.textContent = res.error || "Failed";
                    }
                } catch { inviteMsg.textContent = "Error"; }
            };
        }

    } catch (e) { console.error(e); }
}

async function loadGroupBmcs(groupId) {
    const listContent = document.getElementById('bmcs-list-content');
    const createBtn = document.getElementById('create-group-bmc');
    const newNameInput = document.getElementById('new-group-bmc-name');
    const token = getToken();

    listContent.innerHTML = 'Loading shared BMCs…'; 
    try {
        const r = await fetch(API(`/groups/${groupId}/bmcs`), { headers: { 'Authorization': `Bearer ${token}` }});
        const data = await r.json();
        
        if (!Array.isArray(data) || data.length === 0) {
            listContent.innerHTML = '<p>No shared BMCs yet.</p>';
        } else {
            listContent.innerHTML = data.map(b => `
                <div class="bmc-row" style="margin:5px 0;">
                  <button class="button open-group-bmc" data-id="${b.id}" style="width:100%; text-align:left;">
                    <strong>${b.name}</strong> <span class="muted" style="float:right;">${b.updated || ''}</span>
                  </button>
                </div>
            `).join('');
            
            listContent.querySelectorAll('.open-group-bmc').forEach(btn => {
                btn.addEventListener('click', () => {
                    window.location.search = `bmc_id=${btn.dataset.id}`;
                });
            });
        }
    } catch { listContent.innerHTML = 'Error loading BMCs.'; }
    
    if(createBtn) {
        createBtn.onclick = async () => {
            const name = (newNameInput.value || '').trim() || 'Untitled Shared BMC';
            try {
                const r = await fetch(API(`/groups/${groupId}/bmcs`), {
                    method:'POST',
                    headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ name, data: {} })
                });
                const data = await r.json();
                if (r.ok) window.location.search = `bmc_id=${data.id}`;
            } catch { alert('Network error'); }
        };
    }
}

// --- Editor Logic ---

async function setupGroupBmcEditor(groupId, bmcId) {
    const ideaInput = document.getElementById('product-idea');
    const saveBtn = document.getElementById('save-group-bmc-button');
    const saveMsg = document.getElementById('save-group-bmc-msg');
    const token = getToken();
    
    // Load Data
    try {
        const r = await fetch(API(`/groups/${groupId}/bmcs/${bmcId}`), { headers: { 'Authorization': `Bearer ${token}` }});
        if (!r.ok) { alert("Error loading BMC"); return; }
        const b = await r.json();
        
        ideaInput.value = b.name || '';
        // Helper from bmc_page.js logic
        const KEYS = ["key-partners","key-activities","key-resources","value-propositions","customer-relationships","channels","customer-segments","cost-structure","revenue-streams"];
        KEYS.forEach(k => {
            const el = document.getElementById(`${k}-details`);
            if (el) el.value = (b.data && b.data[k]) ? b.data[k] : "";
        });
    } catch { alert("Network Error"); }

    // Save Data
    if(saveBtn) {
        saveBtn.onclick = async () => {
            saveMsg.textContent = "Saving...";
            const name = ideaInput.value;
            const data = {};
            const KEYS = ["key-partners","key-activities","key-resources","value-propositions","customer-relationships","channels","customer-segments","cost-structure","revenue-streams"];
            KEYS.forEach(k => {
                const el = document.getElementById(`${k}-details`);
                data[k] = el ? el.value : "";
            });

            try {
                const r = await fetch(API(`/groups/${groupId}/bmcs`), {
                    method:'POST',
                    headers: { 'Content-Type':'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ id: bmcId, name, data })
                });
                if(r.ok) {
                    saveMsg.textContent = "Saved successfully!";
                    setTimeout(() => saveMsg.textContent = "", 2000);
                } else {
                    saveMsg.textContent = "Save failed.";
                }
            } catch { saveMsg.textContent = "Error saving."; }
        };
    }
}

// Connect AI Buttons in Group View (Re-binds listeners because we are not on bmc.html)
function setupAiButtons() {
    // Example Canvas
    document.getElementById('example-button')?.addEventListener('click', async () => {
        const productIdea = document.getElementById('product-idea').value;
        if(!productIdea) return alert("Please enter a product idea first.");
        
        document.getElementById("loading-circle-container").style.display = 'block';
        const response = await fetch(API('/bmc/example'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_idea: productIdea }),
        });
        const data = await response.json();
        
        // Update fields
        for (const key in data) {
            const element = document.getElementById(key+'-details');
            if (element) element.value = data[key];
        }
        document.getElementById("loading-circle-container").style.display = 'none';
    });

    // Check Correctness
    document.getElementById("correctness-button")?.addEventListener("click", async () => {
        await checkCorrectness(); // Function from index.js (make sure index.js is loaded)
    });

    // Evaluate
    document.getElementById("evaluate-button")?.addEventListener("click", async () => {
        await evaluateAllInputs(); // Function from index.js
    });
    
    // Tips
    document.getElementById("tips-button")?.addEventListener("click", async () => {
        await tipsBusinessModelCanvas(); // Function from index.js
    });
}