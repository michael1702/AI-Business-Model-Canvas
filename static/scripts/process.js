
// Sichtbarkeit des AI-Containers ein- und ausschalten
function toggleChat() {
  const chatContainer = document.getElementById("chat-container");
  const buttonsContainer = document.getElementById("buttons-container");

  const overlay = document.getElementById("overlay");
  if (chatContainer.style.right === "20px") {
    chatContainer.style.right = "-400px";
    overlay.style.left = "100%";
  } else {
    chatContainer.style.right = "20px";
    overlay.style.left = "calc(100% - 450px)";
  }
  if (buttonsContainer.style.right === "20px") {
    buttonsContainer.style.right = "-400px";
    overlay.style.left = "100%";
  } else {
    buttonsContainer.style.right = "20px";
    overlay.style.left = "calc(100% - 450px)";
  }
}

function toggleButtons() {
  const buttonsContainer = document.getElementById("buttons-container");
  const overlay = document.getElementById("overlay");
  if (buttonsContainer.style.right === "20px") {
    buttonsContainer.style.right = "-400px";
    overlay.style.left = "100%";
  } else {
    buttonsContainer.style.right = "20px";
    overlay.style.left = "calc(100% - 450px)";
  }
}

// Nachricht an den Chat senden und KI-Antwort anzeigen
async function sendMessage(event) {
  const chatInput = document.getElementById("chat-input");
  const message = chatInput.value;

  if (event.type === 'click' || (event.type === 'keydown' && event.key === 'Enter')) { // Abfrage, ob der gewählte input ein click oder eine Entereingabe ist
    event.preventDefault(); //Verhindern der default form behavior, wenn der Benutzer Enter drückt.
    if (!message) return;

    // Ladekreis anzeigen
    document.getElementById("loading-circle-container").style.display = 'block';

    // Chathistory laden und formatieren
  
    const chatHistory = document.querySelectorAll(".chat-message");
    const messages = [];
    chatHistory.forEach(message => {
      const role = message.classList.contains("user-message") ? "user" : "assistant";
      const content = message.textContent.slice(role === "user" ? 6 : 7); // Remove the "User: " or "GPT-4: " part
      messages.push({ role, content });
    });

    const response = await fetch("/chat_with_gpt4", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages: messages, new_message: message }),
    });

    const data = await response.json();
    const reply = data.reply;
    let formattedMessage = reply.replace(/\n/g, '<br>');

    // Ladekreis ausblenden
    document.getElementById("loading-circle-container").style.display = 'none';
    const chatHistoryContainer = document.getElementById("chat-history");
    chatHistoryContainer.innerHTML += `<div class="chat-message user-message">User: ${message}</div>`;
    chatHistoryContainer.innerHTML += `<div class="chat-message ai-message">ChatGPT: ${formattedMessage}</div>`;

    chatInput.value = "";

  }
}


//Event Listener für den Chat senden Button
const sendButton = document.getElementById("send-button");
sendButton.addEventListener("click", async (event) => {
  await sendMessage(event);
});

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

//Funktion um die Building blocks in der Sidebar aufzuklappen
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
