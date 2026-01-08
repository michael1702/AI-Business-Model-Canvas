document.addEventListener('DOMContentLoaded', async () => {
    // 1. Auth Check
    if (typeof ensureAuthUI === 'function') ensureAuthUI(); 

    const token = getToken();
    if (!token) {
        window.location.href = '/auth';
        return;
    }

    // 2. Helper für Auth Headers
    const getAuthHeaders = () => ({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    });

    // 3. Group ID sicher holen
    let groupId = null;
    if (typeof GROUP_ID !== 'undefined' && GROUP_ID) {
        groupId = GROUP_ID;
    } else {
        const pathParts = window.location.pathname.split('/');
        // Nimmt das letzte Segment oder das vorletzte, falls Slash am Ende
        groupId = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];
    }

    // 4. Routing Logic
    const path = window.location.pathname;

    // ============================================================
    // VIEW 1: MY GROUPS OVERVIEW (/my-groups)
    // ============================================================
    if (path.includes('/my-groups')) {
        const listEl = document.getElementById('groups-list');
        const msgEl = document.getElementById('groups-msg');

        async function loadGroups() {
            try {
                const res = await fetch(API('/groups'), { headers: getAuthHeaders() });
                if (res.status === 401) return handleAuthError();
                
                const groups = await res.json();

                if (!Array.isArray(groups) || groups.length === 0) {
                    listEl.innerHTML = '<p>No groups yet.</p>';
                    return;
                }

                listEl.innerHTML = groups.map(g => `
                    <div class="bmc-item" onclick="window.location.href='/group-bmcs/${g.id}'" style="cursor:pointer;">
                        <h3>${g.name}</h3>
                        <p>Members: ${g.member_count !== undefined ? g.member_count : '?'}</p>
                        ${g.is_owner ? '<small style="color:green">Owner</small>' : ''}
                    </div>
                `).join('');
            } catch (e) {
                console.error(e);
                if(listEl) listEl.innerText = "Error loading groups.";
            }
        }

        // Create Group Handler
        document.getElementById('create-group')?.addEventListener('click', async () => {
            const nameInput = document.getElementById('new-group-name');
            const name = nameInput.value;
            if (!name) return;

            try {
                const res = await fetch(API('/groups'), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ name })
                });
                
                if (res.ok) {
                    nameInput.value = '';
                    loadGroups(); 
                } else {
                    const err = await res.json();
                    msgEl.innerText = "Error: " + (err.error || "Unknown");
                }
            } catch (e) {
                console.error(e);
            }
        });

        // Init View 1
        loadGroups(); 
    }

    // ============================================================
    // VIEW 2: GROUP DETAILS & BMCs (/group-bmcs/<id>)
    // ============================================================
    if (path.includes('/group-bmcs/')) {
        const listContent = document.getElementById('bmcs-list-content');
        // Check if we are in Editor Mode (URL param bmc_id exists)
        const bmcId = new URLSearchParams(window.location.search).get('bmc_id');

        // --- Functions for View 2 ---

        async function loadGroupDetails() {
            try {
                const res = await fetch(API(`/groups/${groupId}`), { headers: getAuthHeaders() });
                if (!res.ok) throw new Error("Failed to load group");
                
                const group = await res.json();
                const titleEl = document.getElementById('group-title');
                if(titleEl) titleEl.innerText = group.name;
                
                // Render Members
                const tbody = document.getElementById('members-table-body');
                if (tbody) {
                    tbody.innerHTML = group.members.map(m => {
                        let actionHtml = '';
                        if (m.is_owner) {
                            actionHtml = '<span style="color: #888; font-style: italic;">Owner</span>';
                        } else {
                            actionHtml = `<button onclick="removeMember('${m.id}')" style="color: red; cursor: pointer;">Remove</button>`;
                        }
                        return `
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 10px;">${m.email || 'Unknown User'}</td>
                            <td style="padding: 10px;">${m.is_owner ? 'Owner' : 'Member'}</td>
                            <td style="padding: 10px; text-align: right;">${actionHtml}</td>
                        </tr>
                        `;
                    }).join('');
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function loadGroupBmcs() {
            try {
                const res = await fetch(API(`/groups/${groupId}/bmcs`), { headers: getAuthHeaders() });
                const bmcs = await res.json();

                if (!Array.isArray(bmcs) || bmcs.length === 0) {
                    if(listContent) listContent.innerHTML = '<p>No shared BMCs yet.</p>';
                    return;
                }
                
                if(listContent) {
                    listContent.innerHTML = bmcs.map(b => {
                        // URL with ID parameter for editor mode
                        const bmcUrl = `/group-bmcs/${groupId}?bmc_id=${b.id}`;
                        return `
                        <div class="bmc-item" onclick="window.location.href='${bmcUrl}'" style="cursor:pointer;">
                            <h3>${b.name}</h3>
                            <p>Last updated: ${b.updated || 'Never'}</p>
                        </div>
                        `;
                    }).join('');
                }
            } catch (e) {
                console.error(e);
            }
        }

        // Global functions for HTML access (onclick)
        window.addMember = async function() {
            const emailInput = document.getElementById('new-member-email'); 
            const msg = document.getElementById('member-msg');
            
            if (!emailInput) return;
            const email = emailInput.value.trim();
            if (!email) return;
            
            msg.innerText = "Adding...";
            msg.style.color = "blue";

            try {
                const res = await fetch(API(`/groups/${groupId}/members`), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ email: email })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    msg.innerText = "User added successfully!";
                    msg.style.color = "green";
                    emailInput.value = "";
                    loadGroupDetails(); 
                } else {
                    msg.innerText = data.error || "Failed to add user.";
                    msg.style.color = "red";
                }
            } catch (e) {
                msg.innerText = "Network error.";
                msg.style.color = "red";
            }
        };

        window.removeMember = async function(userId) {
            if (!confirm("Are you sure you want to remove this user?")) return;
            try {
                const res = await fetch(API(`/groups/${groupId}/members/${userId}`), {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
                if (res.ok) {
                    loadGroupDetails(); 
                } else {
                    alert("Could not remove user");
                }
            } catch (e) {
                console.error(e);
            }
        };

        // Create BMC Button Logic
        document.getElementById('create-group-bmc')?.addEventListener('click', async () => {
            const nameInput = document.getElementById('new-group-bmc-name');
            const name = nameInput.value;
            if (!name) return;
            
            const res = await fetch(API(`/groups/${groupId}/bmcs`), {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ name, data: {} })
            });
            
            if (res.ok) {
                const newBmc = await res.json();
                // Redirect to editor mode with new ID
                window.location.href = `/group-bmcs/${groupId}?bmc_id=${newBmc.id}`;
            }
        });

        // --- EDITOR LOGIC ---
        if (bmcId) {
            // Wir sind im Editor Modus -> Verstecke Liste, Zeige Canvas
            const overview = document.getElementById('group-overview-section');
            const editor = document.getElementById('group-bmc-editor');
            
            if(overview) overview.style.display = 'none';
            if(editor) editor.style.display = 'block';
            
            // Load Specific BMC Data
            const res = await fetch(API(`/groups/${groupId}/bmcs/${bmcId}`), {
                headers: getAuthHeaders()
            });
            
            if (res.ok) {
                const bmc = await res.json();
                fillCanvasInputs(bmc.data); // Fülle Textareas
                const titleInput = document.getElementById('product-idea');
                if(titleInput) titleInput.value = bmc.name;
            }

            // Save Button Logic
            const saveBtn = document.getElementById('save-group-bmc-button');
            if(saveBtn) {
                saveBtn.addEventListener('click', async () => {
                    const data = getCanvasData(); 
                    const nameInput = document.getElementById('product-idea');
                    const name = nameInput ? nameInput.value : "Untitled";
                    
                    const msg = document.getElementById('save-group-bmc-msg');
                    msg.innerText = "Saving...";
                    msg.style.color = "blue";

                    try {
                        const saveRes = await fetch(API(`/groups/${groupId}/bmcs`), {
                            method: 'POST',
                            headers: getAuthHeaders(),
                            body: JSON.stringify({ id: bmcId, name, data })
                        });
                        
                        if (saveRes.ok) {
                            msg.innerText = "Saved successfully!";
                            msg.style.color = "green";
                            setTimeout(() => msg.innerText = "", 2000);
                        } else {
                            msg.innerText = "Error saving.";
                            msg.style.color = "red";
                        }
                    } catch(e) {
                        console.error(e);
                        msg.innerText = "Network Error";
                    }
                });
            }

        } else {
            // Wir sind im Listen Modus -> Lade Listen
            loadGroupDetails();
            loadGroupBmcs();
        }
    }

    // --- SHARED HELPER FUNCTIONS ---

    function getCanvasData() {
        const data = {};
        document.querySelectorAll('textarea').forEach(ta => {
            if(ta.id && ta.id.includes('-details')) {
                const key = ta.id.replace('-details', '');
                data[key] = ta.value;
            }
        });
        return data;
    }
    window.getCanvasData = getCanvasData;

    function fillCanvasInputs(data) {
        if (!data) return;
        for (const [key, val] of Object.entries(data)) {
            const el = document.getElementById(key + '-details');
            if (el) el.value = val;
        }
    }

    function handleAuthError() {
        console.log("Token invalid, redirecting...");
        window.location.href = '/auth';
    }
});