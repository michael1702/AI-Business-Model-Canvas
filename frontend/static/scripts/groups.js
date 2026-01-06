document.addEventListener('DOMContentLoaded', async () => {
    ensureAuthUI(); // Auth check from index.js

    const token = getToken();
    if (!token) {
        window.location.href = '/auth';
        return;
    }

    // ID sicher holen (Fallback Logik)
    let groupId = null;
    if (typeof GROUP_ID !== 'undefined' && GROUP_ID) {
        groupId = GROUP_ID;
    } else {
        const pathParts = window.location.pathname.split('/');
        // Nimmt das letzte Segment oder das vorletzte, falls Slash am Ende
        groupId = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];
    }

    const getAuthHeaders = () => ({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    });

    // Prüfen, auf welcher Seite wir sind
    const path = window.location.pathname;

    // --- VIEW 1: My Groups Overview (/my-groups) ---
    if (path.includes('/my-groups')) {
        const listEl = document.getElementById('groups-list');
        const msgEl = document.getElementById('groups-msg');

        // Funktion definieren
        async function loadGroups() {
            try {
                const res = await fetch(API('/groups'), {
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
                        <p>Members: ${g.member_count !== undefined ? g.member_count : '?'}</p>
                        ${g.is_owner ? '<small style="color:green">Owner</small>' : ''}
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
                const res = await fetch(API('/groups'), {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ name })
                });
                
                if (res.ok) {
                    nameInput.value = '';
                    loadGroups(); // Liste neu laden
                } else {
                    const err = await res.json();
                    msgEl.innerText = "Error: " + (err.error || "Unknown");
                }
            } catch (e) {
                console.error(e);
            }
        });

        // WICHTIG: Automatisch laden beim Start!
        loadGroups(); 
    }

    // --- VIEW 2: Group Details & BMCs (/group-bmcs/<id>) ---
    if (path.includes('/group-bmcs/')) {
        const listContent = document.getElementById('bmcs-list-content');
        const bmcId = new URLSearchParams(window.location.search).get('bmc_id');

        async function loadGroupDetails() {
            try {
                const res = await fetch(API(`/groups/${groupId}`), { headers: getAuthHeaders() });
                if (!res.ok) throw new Error("Failed to load group");
                
                const group = await res.json();
                document.getElementById('group-title').innerText = group.name;
                
                // Render Members
                const tbody = document.getElementById('members-table-body');
                if (tbody) {
                    tbody.innerHTML = group.members.map(m => {
                        let actionHtml = '';
                        if (m.is_owner) {
                            actionHtml = '<span style="color: #888; font-style: italic;">Owner</span>';
                        } else {
                            // "Remove" Button nur anzeigen
                            actionHtml = `<button onclick="removeMember('${m.id}')" style="color: red; cursor: pointer;">Remove</button>`;
                        }

                        return `
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 10px;">${m.email}</td>
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

        // Add Member (Global gemacht für HTML Zugriff)
        window.addMember = async function() {
            // FIX: Zuerst definieren, dann benutzen!
            const emailInput = document.getElementById('new-member-email'); 
            const msg = document.getElementById('member-msg');
            
            if (!emailInput) return; // Sicherheitscheck
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
                    loadGroupDetails(); // Liste neu laden
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
                        const bmcUrl = `/group/${groupId}/bmc/${b.id}`;
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

        // Initialisierung View 2
        if (!bmcId) {
            loadGroupDetails();
            loadGroupBmcs();
        } else {
            // Falls wir im Editor-Modus sind (BMCs bearbeiten), laden wir hier ggf. Editor-Logik
            // (Code dafür hast du wahrscheinlich schon an anderer Stelle oder in index.js)
        }
    }

    function handleAuthError() {
        console.log("Token invalid, redirecting...");
        window.location.href = '/auth';
    }
});