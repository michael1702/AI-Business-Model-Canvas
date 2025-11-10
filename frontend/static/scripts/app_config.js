// API + token helpers (persist in localStorage)
window.API = (p) => `/api/v1${p}`;

window.getToken   = () => localStorage.getItem('token');
window.setToken   = (t) => localStorage.setItem('token', t);
window.clearToken = () => localStorage.removeItem('token');

// auth-aware visibility
window.ensureAuthUI = () => {
  const has = !!getToken();
  
  document.querySelectorAll('[data-auth="guest"]').forEach(n => n.style.display = has ? 'none' : '');
  document.querySelectorAll('[data-auth="user"]').forEach(n => n.style.display = has ? '' : 'none');
};

//Sidebar aktivieren oder deaktivieren
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

//Eventlistener für Sidebar Toggle, welcher den Hauptcontainer verschiebt
document.querySelector(".sidebar-toggle").addEventListener("click", function() {
  const mainContent = document.querySelector("#main-content");
  const sidebarMenu = document.querySelector(".sidebar-menu");

  sidebarMenu.classList.toggle("open");
  mainContent.classList.toggle("sidebar-open");
});

//Funktion um die Building blocks aufzuklappen
function toggleBuildingBlocks() {
  const buildingBlocksMenu = document.getElementById("building-blocks-menu");
  const buildingBlocksArrow = document.getElementById("building-blocks-arrow");
  if (buildingBlocksMenu.style.display === "none") {
    buildingBlocksMenu.style.display = "block";
    buildingBlocksArrow.innerHTML = "&#x25BC;";
  } else {
    buildingBlocksMenu.style.display = "none";
    buildingBlocksArrow.innerHTML = "&#x25B6;";
  }
}
