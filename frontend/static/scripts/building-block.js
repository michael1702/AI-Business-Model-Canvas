// Lade die gespeicherten Building Block Details vom local Storage
function loadSavedDetails(blockType, blockTitle) {
  const savedInputData = localStorage.getItem("inputData");
  const span = document.querySelector(".block-title");
  const id = span.getAttribute("id");
  const savedTitle = localStorage.getItem(blockType+"-title");
  if (savedInputData) {
    const inputData = JSON.parse(savedInputData);
    if (inputData[blockType]) {
      document.getElementById("block-details").value = inputData[blockType];
    }
  }
  if (savedTitle !== null) {
    span.innerText = savedTitle;
  } else {
    span.innerText = blockTitle;
  }
  loadNotes(blockType);
}

// Chat Containers Sichtbarkeit ein- und ausschalten
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

    console.log(messages);

    const response = await fetch(API("/chat"), {
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


// Speicher die Building Block Details (Inputs) im local storage
function saveDetails(blockType) {
  const blockDetails = document.getElementById("block-details").value;
  if (blockDetails) {
    const inputData = JSON.parse(localStorage.getItem("inputData")) || {};
    inputData[blockType] = blockDetails;
    localStorage.setItem("inputData", JSON.stringify(inputData));
    alert("Saved successfully!");
  }
}

//Evaluierfunktion: Sende eine Anfrage an GPT, den aktuellen Building Block zu evaluieren.
async function evaluateBuildingBlock(blockType) {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  //Laden der Produktidee und der Building block details vom local storage und den Chat input vom Input Feld
  const productIdea = localStorage.getItem("product-idea");
  const blockDetails = document.getElementById("block-details").value;
  let chatInput = document.getElementById("chat-input").value;
  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Evaluate my current Idea.";
  }
  // Check, ob alle benötigten Felder befüllt sind
  if (!productIdea || !blockDetails) {
    alert("Please ensure all fields are filled");
    return;
  }
  // API Anfrage der Evaluation
  const response = await fetch(API("/bmc/evaluate_block"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ product_idea: productIdea, building_block: blockType, building_block_input: blockDetails, chat_input: chatInput})
  });

  // API Antwort auswerten und dem Chatverlauf hinzufügen
  const data = await response.json();
  const evaluationResult = data.evaluation_result;
  let formattedMessage = evaluationResult.replace(/\n/g, '<br>');

  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
  // Evaluation anzeigen
  const chatHistoryContainer = document.getElementById("chat-history");
  chatHistoryContainer.innerHTML += `<div class="user-message">User: ${chatInput}</div>`;
  chatHistoryContainer.innerHTML += `<div class="ai-message">ChatGPT: ${formattedMessage}</div>`;

  const chatContainer = document.getElementById("chat-container");
}

//Tippfunktion: Sende eine Anfrage an GPT, um für die Entwicklung des aktuellen Building Block Tipps zu erhalten.
async function tipsBuildingBlock(blockType,blockTitle) {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  //Laden der Produktidee und der Building block details vom local storage und den Chat input vom Input Feld
  const productIdea = localStorage.getItem("product-idea");
  const blockDetails = document.getElementById("block-details").value;
  let chatInput = document.getElementById("chat-input").value;
  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = `Give me tips for developing the ${blockTitle}.`;
  }
  // API Anfrage nach Tipps
  const response = await fetch(API("/bmc/tips_block"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ product_idea: productIdea, building_block: blockType, building_block_input: blockDetails, chat_input: chatInput})
  });

  // API Antwort auswerten und dem Chatverlauf hinzufügen
  const data = await response.json();
  const tipsResult = data.tips_result;
  let formattedMessage = tipsResult.replace(/\n/g, '<br>');

  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
  // Tipps anzeigen
  const chatHistoryContainer = document.getElementById("chat-history");
  chatHistoryContainer.innerHTML += `<div class="user-message">User: ${chatInput}</div>`;
  chatHistoryContainer.innerHTML += `<div class="ai-message">ChatGPT: ${formattedMessage}</div>`;

  const chatContainer = document.getElementById("chat-container");
}


//Beispielcanvas für aktuelles Produkt anfordern
async function prefillBuildingBlock(blockType) {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  const product_idea = localStorage.getItem("product-idea");

  const response = await fetch(API('/bmc/prefill'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ "product_idea" : product_idea, "building_block" : blockType }),
  });
  const prefilledBlock =  await response.json();
  const element = document.getElementById('block-details');

  if (element) {;
    element.value = prefilledBlock[blockType];
  }
  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
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

//Funktion, um einen Popup-Text zu aktivieren/deaktivieren 
function togglePopupText(elementId, button) {
  const popup = document.getElementById(elementId);

  if (popup.style.display === "none") {
    closeAllPopups();
    popup.style.display = "block";
    button.classList.add("active");
  } else {
    popup.style.display = "none";
    button.classList.remove("active");
  }
}

// Eventlistener für die Aktivierung der Buttons
document.querySelectorAll(".popup-button").forEach((button) => {
  button.addEventListener("click", () => {
    togglePopupText(button.dataset.target, button);
  });
});


//Funktion zur Schließung aller Popupbuttons
function closeAllPopups() {
  document.querySelectorAll(".popup-text").forEach((popup) => {
    popup.style.display = "none";
  });
  document.querySelectorAll(".popup-button").forEach((button) => {
    button.classList.remove("active"); // Remove the "active-button" class
  });
}

// Speicher die Notizen der Building Block Unterseite im Local Storage
function saveNotes(blockType) {
  const noteDetails = document.getElementById("note-details").value;
  if (noteDetails) {
    localStorage.setItem(blockType + "-notes", noteDetails);
  }
}

// Lade die Notizen der Unterseite aus dem Local Storage
function loadNotes(blockType) {
  const savedNotes = localStorage.getItem(blockType + "-notes");
  if (savedNotes) {
    document.getElementById("note-details").value = savedNotes;
  }
}

// Add this event listener to your existing JS code
document.getElementById("note-details").addEventListener("blur", () => {
  saveNotes(blockType);
});