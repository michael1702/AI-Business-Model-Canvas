// Lade die gespeicherten Building Block Details vom local Storage
function loadSavedDetails() {
    const savedInputData = localStorage.getItem("inputData");

    //Erstmal die Value Proposition Daten abrufen
    if (savedInputData) {
      const inputData = JSON.parse(savedInputData);
      if (inputData["value-propositions"]) {
        document.getElementById("valprop-details").value = inputData["value-propositions"];
      }
    }

    //Dann die Customer Segment Daten abrufen
    if (savedInputData) {
      const inputData = JSON.parse(savedInputData);
      if (inputData["customer-segments"]) {
        document.getElementById("custseg-details").value = inputData["customer-segments"];
      }
    }

    // Gespeicherte VPC Felder abrufen und als text-placeholder setzen
    const savedInputDataVpc = localStorage.getItem("inputData-vpc");
    if (savedInputDataVpc) {
      const inputDataVpc = JSON.parse(savedInputDataVpc);
      const canvasBlocks = document.querySelectorAll(".canvas-block");
      canvasBlocks.forEach((block) => {
        const textarea = block.querySelector("textarea");
        const blockName = block.className.split(" ")[1];
        const savedValue = inputDataVpc[blockName];
        if (savedValue) {
          textarea.value = savedValue;
        }
      });
    }
}

// Automatische textarea-Größe je nach Input
function resizeTextarea(textarea) {
  textarea.style.height = 'auto'; // Reset the height to auto before calculating the new height
  textarea.style.height = textarea.scrollHeight + 'px'; // Set the new height based on scroll height
}

//Event-Listener für Resize Textarea
document.addEventListener('DOMContentLoaded', function () {
  const textareas = document.querySelectorAll('textarea');
  textareas.forEach((textarea) => {
    textarea.addEventListener('input', function () {
      resizeTextarea(textarea);
    });
    resizeTextarea(textarea); // Call once to resize on page load
  });
});

// Speicherfunktion: Speichere die inputs im local Storage
function saveInput(canvasBlock, inputValue) {
  if (canvasBlock === "value-propositions" || canvasBlock === "customer-segments") {
    const savedInputData = localStorage.getItem("inputData");
    const inputData = savedInputData ? JSON.parse(savedInputData) : {};
    inputData[canvasBlock] = inputValue;
    localStorage.setItem("inputData", JSON.stringify(inputData));
  } else {
    const savedInputDataVpc = localStorage.getItem("inputData-vpc");
    const inputDataVpc = savedInputDataVpc ? JSON.parse(savedInputDataVpc) : {};
    inputDataVpc[canvasBlock] = inputValue;
    localStorage.setItem("inputData-vpc", JSON.stringify(inputDataVpc));
  }
}

// Eventlistener für den Speicherbutton
document.querySelector(".save-button").addEventListener("click", () => {
  // Speicher alle Value Proposition Canvas Blöcke Details, wenn der jeweilige input gefüllt wurde
  const feld = document.querySelectorAll(".canvas-block");
  feld.forEach((block) => {
    const input = block.querySelector("textarea");
    if (input.value) {
      const canvasBlock = block.classList[1];
      saveInput(canvasBlock, input.value);
    }
  });

  //Speicher die Value Propositions und Customer Segments
  const valPropInput = document.getElementById("valprop-details");
  if (valPropInput.value) {
    saveInput("value-propositions", valPropInput.value);
  }

  const custSegInput = document.getElementById("custseg-details");
  if (custSegInput.value) {
    saveInput("customer-segments", custSegInput.value);
  }
  console.log(JSON.stringify(localStorage.getItem("inputData-vpc")))
  alert("Saved successfully!");
});



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
  
      // Chat Historie herausziehen
    
      const chatHistory = document.querySelectorAll(".chat-message");
      const messages = [];
      chatHistory.forEach(message => {
        const role = message.classList.contains("user-message") ? "user" : "assistant";
        const content = message.textContent.slice(role === "user" ? 6 : 7); // Entfernen des "User: " oder "ChatGPT: " 
        messages.push({ role, content });
      });
  
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

//Funktion um ein Value Proposition Canvas Beispiel zu bekommen
async function getValuePropositionCanvas(productIdea, valuePropositions, customerSegments) {
  const response = await fetch(API('/vpc/example'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ productIdea, valuePropositions, customerSegments }),
  });
  return await response.json();
}

//Funktion zum Updaten des Value Proposition Canvas 
function updateValuePropositionCanvas(data) {
  for (const key in data) {
    const element = document.getElementById(key+'-details');
    if (element) {
      element.value = data[key];
    }
  }
}

//Tippfunktion: Sende eine Anfrage an GPT, um für die Entwicklung des Business Model Canvas Tipps zu erhalten.
async function tipsFunction() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  //Laden der Produktidee und der Building block details vom local storage und den Chat input vom Input Feld
  const productIdea = localStorage.getItem("product-idea");
  let chatInput = document.getElementById("chat-input").value;
  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = `Give me tips for developing the Value Proposition Canvas.`;
  }
  // API Anfrage nach Tipps
  const response = await fetch(API("/vpc/tips"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ product_idea: productIdea, chat_input: chatInput})
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

}

//Event-Listener für Tipps
document.getElementById("tips-button").addEventListener("click", async () => {
  await tipsFunction();
});

//Check auf Korrektheit: Sende eine Anfrage an GPT, den aktuellen BMC auf Syntaxfehler und Fehler bei dem Ausfüllen.
async function checkCorrectness() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const buildingBlocks = document.querySelectorAll(".canvas-block");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Check the Correctness of by Value Proposition Canvas.";
  }

  buildingBlocks.forEach((block) => {
    const input = block.querySelector('textarea');
    if (input && input.value) {
      inputsData[block.classList[1]] = input.value;
    }
  });

  const response = await fetch(API("/vpc/check_correctness"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({product_idea: productIdea, chat_input: chatInput, inputs_data: inputsData}),
  });

  // API Antwort auswerten und dem Chatverlauf hinzufügen
  const data = await response.json();
  const checkResult = data.check_result;
  let formattedMessage = checkResult.replace(/\n/g, '<br>');

  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
  // Evaluation anzeigen
  const chatHistoryContainer = document.getElementById("chat-history");
  chatHistoryContainer.innerHTML += `<div class="user-message">User: ${chatInput}</div>`;
  chatHistoryContainer.innerHTML += `<div class="ai-message">ChatGPT: ${formattedMessage}</div>`;

};

//Event-Listener für Checkfunktion
document.getElementById("correctness-button").addEventListener("click", async () => {
await checkCorrectness();
});


//Evaluierfunktion: Sende eine Anfrage an GPT, den aktuellen VPC zu evaluieren.
async function evaluateAllInputs() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const canvasBlocks = document.querySelectorAll(".canvas-block");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Evaluate my current Value Proposition Canvas.";
  }

  canvasBlocks.forEach((block) => {
    const input = block.querySelector('textarea');
    if (input && input.value) {
      inputsData[block.classList[1]] = input.value;
    }
  });


  console.log(inputsData);

  const response = await fetch(API("/vpc/evaluate"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({product_idea: productIdea, chat_input: chatInput, inputs_data: inputsData}),
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

}

//Event-Listener für Evaluierfunktion
document.getElementById("evaluate-button").addEventListener("click", async () => {
  await evaluateAllInputs();
});

//Event Listener für Beispiel Value proposition Canvas Button
document.getElementById('example-button').addEventListener('click', async () => {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';
  const productIdea = localStorage.getItem("product-idea");
  const valuePropositions = document.getElementById('valprop-details').value;
  const customerSegments = document.getElementById('custseg-details').value;
  const exampleValuePropCanvasData = await getValuePropositionCanvas(productIdea, valuePropositions, customerSegments);
  updateValuePropositionCanvas(exampleValuePropCanvasData);
  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
});

// Export to PNG, welches Pre-Elemente benutzt, damit Textareas richtig angezeigt werden und nicht nach 1 Zeile abgeschnitten werden
document.getElementById("export-button").addEventListener("click", function () {
  const element = document.getElementById("main-content");

  // Verstecke die Help, Notes und Trigger Questions Area
  const helpContainer = document.getElementById("help-container");
  const noteContainer = document.getElementById("note-container");
  const triggerQuestionsContainer = document.getElementById("trigger-questions-container");
  helpContainer.style.display = "none";
  noteContainer.style.display = "none";
  triggerQuestionsContainer.style.display = "none";
  
  
  // Finde alle Textarea Elemente
  const textareas = element.querySelectorAll("textarea");
  const preElements = [];

  // Ersetze textareas mit den Pre Elements
  textareas.forEach(textarea => {
    const pre = document.createElement("pre");
    pre.innerText = textarea.value;
    pre.style.whiteSpace = "pre-wrap";
    pre.style.fontFamily = textarea.style.fontFamily;
    pre.style.fontSize = textarea.style.fontSize;
    pre.style.border = "1px solid #ccc";
    pre.style.padding = "10px";
    pre.style.marginBottom = "10px";
    pre.style.borderRadius = "5px";
    pre.style.wordWrap = "break-word";

    textarea.parentNode.replaceChild(pre, textarea);
    preElements.push(pre);
  });

  var opt = {
    scale: 2,
    width: element.offsetWidth,
    height: element.offsetHeight,
    scrollY: 0,
    scrollX: 0,
    backgroundColor: null,
  };

  // Speicher den Canvas für den User
  html2canvas(element, opt).then(function (canvas) {
    //Ersetze die Pre Elements mit den originalen Textareas, setze die Help, Notes und Trigger Questions Area wieder auf sichtbar
    preElements.forEach((pre, index) => {
      pre.parentNode.replaceChild(textareas[index], pre);
    });
    helpContainer.style.display = "block";
    noteContainer.style.display = "block";
    triggerQuestionsContainer.style.display = "none";

    const link = document.createElement("a");
    link.download = "mycanvas.png";
    link.href = canvas.toDataURL();
    link.click();
  });
});



function toggleNoteWindow() {
  const noteContainer = document.getElementById("note-container");
  if (noteContainer.style.bottom === "20px") {
    noteContainer.style.bottom = "-600px";
  } else {
    noteContainer.style.bottom = "20px";
  }
}

function saveNotesToLocalStorage() {
  const noteText = document.getElementById("note-text").value;
  if (noteText) {
    localStorage.setItem("notes-vpc", noteText);
  }
}

function loadNotesFromLocalStorage() {
  const savedNotes = localStorage.getItem("notes-vpc");
  if (savedNotes) {
    document.getElementById("note-text").value = savedNotes;
  }
}

// Eventlistener der die Notizen beim Laden der Seite aus dem Local Storage lädt 
window.addEventListener("load", loadNotesFromLocalStorage);


function toggleTriggerQuestionsWindow() {
  const triggerQuestionsContainer = document.getElementById("trigger-questions-container");
  if (triggerQuestionsContainer.style.bottom === "20px") {
    triggerQuestionsContainer.style.bottom = "-600px";
  } else {
    triggerQuestionsContainer.style.bottom = "20px";
  }
}

//Help-Fenster
function toggleHelpWindow() {
  const helpContainer = document.getElementById("help-container");
  if (helpContainer.style.bottom === "20px") {
    helpContainer.style.bottom = "-600px";
  } else {
    helpContainer.style.bottom = "20px";
  }
}
