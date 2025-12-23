
document.addEventListener('DOMContentLoaded', async () => {
    ensureAuthUI(); // Auth check from index.js

    const token = getToken();
    if (!token) {
        window.location.href = '/auth';
        return;
    }

    // Helper function for headers with token
    const getAuthHeaders = () => ({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    });

    const path = window.location.pathname;

    // --- VIEW 1: My Groups Overview (/my-groups) ---
    if (path.includes('/my-groups')) {
        const listEl = document.getElementById('groups-list');
        const msgEl = document.getElementById('groups-msg');

        // Load groups
        async function loadGroups() {
            try {
                const res = await fetch(API('/groups/'), {
                    headers: getAuthHeaders()
                });
                if (res.status === 401) return handleAuthError();
                const groups = await res.json();

                if (!Array.isArray(groups) || groups.length === 0) {
                    listEl.innerHTML = '<p>No groups yet.</p>';
                    return;
                }

                listEl.innerHTML = groups.map(g => `
                    <div class="bmc-item" onclick="window.location.href='/group-bmcs/${g.id}'" style="cursor:pointer;">
                        <h3>${g.name}</h3>
                        <p>Members: ${g.members ? g.members.length : 0}</p>
                    </div>
                `).join('');
            } catch (e) {
                console.error(e);
                listEl.innerText = "Error loading groups.";
            }
        }

        // Create new group
        document.getElementById('create-group')?.addEventListener('click', async () => {
            const nameInput = document.getElementById('new-group-name');
            const name = nameInput.value;
            if (!name) return;

            try {
                const res = await fetch(API('/groups/'), {
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

        await loadGroups();
    }

    // --- VIEW 2: Group Details & BMCs (/group-bmcs/<id>) ---
    if (path.includes('/group-bmcs/')) {
        // Extract ID from URL: /group-bmcs/UUID
        const parts = path.split('/');
        const groupId = parts[parts.length - 1]; // Last part is ID
        const bmcId = new URLSearchParams(window.location.search).get('bmc_id');

        // Elements
        const listContent = document.getElementById('bmcs-list-content');
        const memberList = document.getElementById('members-list');
        const titleHeader = document.getElementById('group-name-header');

        // 1. Load group info & members
        async function loadGroupInfo() {
            try {
                const res = await fetch(API(`/groups/${groupId}`), {
                    headers: getAuthHeaders()
                });
                if (!res.ok) throw new Error("Group not found");
                
                const group = await res.json();
                if(titleHeader) titleHeader.innerText = group.name;

                // Show members
                memberList.innerHTML = (group.members || []).map(m => `<li>👤 ${m}</li>`).join('');
            } catch (e) {
                console.error(e);
                if(titleHeader) titleHeader.innerText = "Error loading group";
            }
        }

        // 2. Load group BMCs
        async function loadGroupBmcs() {
            try {
                const res = await fetch(API(`/groups/${groupId}/bmcs`), {
                    headers: getAuthHeaders()
                });
                const bmcs = await res.json();

                if (!Array.isArray(bmcs) || bmcs.length === 0) {
                    listContent.innerHTML = '<p>No shared BMCs yet.</p>';
                    return;
                }

                listContent.innerHTML = bmcs.map(b => `
                    <div class="bmc-item" onclick="window.location.href='?bmc_id=${b.id}'" style="cursor:pointer;">
                        <strong>${b.name}</strong> <br>
                        <small>Last updated: ${b.updated}</small>
                    </div>
                `).join('');
            } catch (e) {
                console.error(e);
                listContent.innerText = "Error loading BMCs.";
            }
        }

        // 3. Add member
        document.getElementById('invite-member-btn')?.addEventListener('click', async () => {
            const emailInput = document.getElementById('invite-email');
            const email = emailInput.value;
            const msg = document.getElementById('invite-msg');
            
            if (!email) return;

            try {
                const res = await fetch(API(`/groups/${groupId}/members`), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ email })
                });
                const data = await res.json();
                
                if (res.ok) {
                    msg.innerText = "User added!";
                    msg.style.color = "green";
                    emailInput.value = "";
                    loadGroupInfo(); // Refresh list
                } else {
                    msg.innerText = "Error: " + (data.error || "Failed");
                    msg.style.color = "red";
                }
            } catch (e) {
                console.error(e);
            }
        });

        // 4. Create new BMC
        document.getElementById('create-group-bmc')?.addEventListener('click', async () => {
            const name = document.getElementById('new-group-bmc-name').value;
            if (!name) return;
            
            const res = await fetch(API(`/groups/${groupId}/bmcs`), {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ name, data: {} })
            });
            
            if (res.ok) {
                loadGroupBmcs();
                document.getElementById('new-group-bmc-name').value = '';
            }
        });

        // --- EDITOR LOGIC (if bmc_id present) ---
        if (bmcId) {
            document.getElementById('group-overview-section').style.display = 'none';
            document.getElementById('group-bmc-editor').style.display = 'block';
            
            // Load BMC data
            const res = await fetch(API(`/groups/${groupId}/bmcs/${bmcId}`), {
                headers: getAuthHeaders()
            });
            if (res.ok) {
                const bmc = await res.json();
                // Fill the textareas
                fillCanvasInputs(bmc.data); // Function from index.js or defined here
                document.getElementById('product-idea').value = bmc.name;
            }

            // Save button
            document.getElementById('save-group-bmc-button')?.addEventListener('click', async () => {
                const data = getCanvasData(); // Function from index.js
                const name = document.getElementById('product-idea').value || "Untitled";
                
                const saveRes = await fetch(API(`/groups/${groupId}/bmcs`), {
                    method: 'POST', // or PUT if your API supports update
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ id: bmcId, name, data })
                });
                
                const msg = document.getElementById('save-group-bmc-msg');
                if (saveRes.ok) {
                    msg.innerText = "Saved successfully!";
                    setTimeout(() => msg.innerText = "", 2000);
                } else {
                    msg.innerText = "Error saving.";
                }
            });
        } else {
            // Only load lists if not in editor
            await loadGroupInfo();
            await loadGroupBmcs();
        }
    }

    function handleAuthError() {
        console.log("Token invalid, redirecting...");
        window.location.href = '/auth';
    }
});

// Helper functions (if index.js does not make them global)
function getCanvasData() {
    const data = {};
    document.querySelectorAll('textarea').forEach(ta => {
        if(ta.id) data[ta.id.replace('-details', '')] = ta.value;
    });
    return data;
}

function fillCanvasInputs(data) {
    if (!data) return;
    for (const [key, val] of Object.entries(data)) {
        const el = document.getElementById(key + '-details');
        if (el) el.value = val;
    }
}