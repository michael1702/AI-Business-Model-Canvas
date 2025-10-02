// Inhalte in den Browser laden
document.addEventListener("DOMContentLoaded", () => {
  // Gespeicherte Eingaben und Titel laden
  loadSavedInputs();
  loadSavedTitles();
});



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
    // Chatverlauf extrahieren und ins erforderliche Format konvertieren
  
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


// Produktidee im local Storage speichern
function saveProductIdea() {
  const productIdeaInput = document.getElementById("product-idea");
  const productIdea = productIdeaInput.value;
  if (productIdea) {
    localStorage.setItem("product-idea", productIdea);
  }
}

// Produktidee im local Storage speichern
function editTitle(event) {

  if (isInEditMode) {
      event.preventDefault();
      //richtigen Span aussuchen
      const span = event.target.tagName === 'SPAN' ? event.target : event.target.querySelector('span'); 
      
      const currentTitle = span.innerText;
      const newTitle = prompt("Enter a new name for this block:", currentTitle);

      if (newTitle !== null && newTitle !== "") {
          span.innerText = newTitle;
          localStorage.setItem(span.id, newTitle);
      }
      console.log(localStorage.getItem(span.id));

  }
}

// Edit-Mode der Blocktitel ein- oder ausschalten
let isInEditMode = false;
function toggleEditMode() {
  isInEditMode = !isInEditMode;
  const editButton = document.getElementById("edit-button");
  editButton.innerText = isInEditMode ? "Done" : "Edit Building Blocks";
  const blockTitles = document.querySelectorAll(".block-title");
  }


//Eventlistener für Edit Funktion an oder ausschalten, wenn im Editmode
const buildingBlocks = document.querySelectorAll(".building-block");
buildingBlocks.forEach((block) => {
  const blockTitle = block.querySelector(".block-title");
  if (isInEditMode) {
      blockTitle.addEventListener("click", editTitle);
  } else {
      blockTitle.removeEventListener("click", editTitle);
  }
});

//Inputwerte aus dem Local Storage laden und als Placeholder setzen
function loadSavedInputs() {
  const product_idea = document.querySelector("#product-idea");
  const saved_product_idea = localStorage.getItem("product-idea");
  if(saved_product_idea) {
    product_idea.value = saved_product_idea;
  }
  const buildingBlocks = document.querySelectorAll(".building-block");
  buildingBlocks.forEach((block) => {
    const textarea = block.querySelector("textarea");
    const blockName = block.className.split(" ")[1];
    const savedInputData = localStorage.getItem("inputData");
    if (savedInputData) {
      const inputData = JSON.parse(savedInputData);
      const savedValue = inputData[blockName];
      if (savedValue) {
        textarea.value = savedValue;
      }
    }
  });
  console.log(JSON.parse(localStorage.getItem("inputData")));
}

//Lade gespeicherte Titel aus dem local storage und überschreibe die dazugehörige Span in der HTML
function loadSavedTitles() {
  const buildingBlocks = document.querySelectorAll('.building-block');
  
  buildingBlocks.forEach(block => {
    const id = block.querySelector('span').getAttribute('id');
    const savedTitle = localStorage.getItem(id);
    if (savedTitle !== null) {
      block.querySelector('span').innerText = savedTitle;
    }
  });
}


// Lade die gespeicherten Inputs von den Subseiten von dem local Storage
document.addEventListener("DOMContentLoaded", () => {
  const savedInputData = localStorage.getItem("inputData");
  if (savedInputData) {
    const inputData = JSON.parse(savedInputData);
    if (inputData["key-partners"]) {
      document.getElementById("key-partners-details").value = inputData["key-partners"];
    }
  }
});

document.addEventListener("DOMContentLoaded", loadSavedInputs);

// Speicherfunktion: Speichere die inputs im local Storage
function saveInput(buildingBlock, inputValue) {
  inputData[buildingBlock] = inputValue;
  localStorage.setItem("inputData", JSON.stringify(inputData));
  console.log(JSON.stringify(inputData))
}

// Eventlistener für den Speicherbutton der Key Partner Details und Produktidee im local Störage --> ERWEITERN
document.querySelector(".save-button").addEventListener("click", () => {
  saveProductIdea(); // Speicher die Produktidee
  
  // Speicher alle building block Details, wenn der jeweilige input gefüllt wurde
  const buildingBlocks = document.querySelectorAll('.building-block');
  buildingBlocks.forEach(block => {
  const input = block.querySelector('textarea');
  if (input.value) {
  inputData[block.classList[1]] = input.value;
  localStorage.setItem("inputData", JSON.stringify(inputData));
  }
  });
  alert("Saved successfully!")
  console.log(JSON.stringify(inputData))
  });


//Event Listener für den Chat senden button
const sendButton = document.getElementById("send-button");
sendButton.addEventListener("click", async (event) => {
  await sendMessage(event);
});

//Beispielcanvas für aktuelles Produkt anfordern
async function getExampleCanvas(product_idea) {
  const response = await fetch('/example_canvas_by_product', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_idea }),
  });
  return await response.json();
}

//Building blocks updaten
function updateBuildingBlocks(data) {
  console.log(JSON.stringify(data))
  for (const key in data) {
    const element = document.getElementById(key+'-details');
    if (element) {
      element.value = data[key];
    }
  }
}

//Event Listener für den Example Button
const exampleButton = document.getElementById('example-button');
exampleButton.addEventListener('click', async (event) => {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  const productIdea = document.getElementById('product-idea').value;
  const exampleCanvasData = await getExampleCanvas(productIdea);
  updateBuildingBlocks(exampleCanvasData);
  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';

});

//Check auf Korrektheit: Sende eine Anfrage an GPT, den aktuellen BMC auf Syntaxfehler und Fehler bei dem Ausfüllen.
async function checkCorrectness() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const buildingBlocks = document.querySelectorAll(".building-block");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Check the Correctness of by Business Model Canvas.";
  }

  buildingBlocks.forEach((block) => {
    const input = block.querySelector('textarea');
    if (input && input.value) {
      inputsData[block.classList[1]] = input.value;
    }
  });

  const response = await fetch("/check_correctness", {
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

//Evaluierfunktion: Sende eine Anfrage an GPT, den aktuellen BMC zu evaluieren.
async function evaluateAllInputs() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const buildingBlocks = document.querySelectorAll(".building-block");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Evaluate my current Idea.";
  }

  buildingBlocks.forEach((block) => {
    const input = block.querySelector('textarea');
    if (input && input.value) {
      inputsData[block.classList[1]] = input.value;
    }
  });


  console.log(inputsData);

  const response = await fetch("/evaluate_all_inputs", {
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

//Business Model Patterns: Sende eine Anfrage an GPT, Business model Patterns für die Produktidee zu nennen.
async function getBusinessModelPatterns() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Give me Business Model Patterns for my current Idea.";
  }

  console.log(inputsData);

  const response = await fetch("/get_business_model_patterns", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({product_idea: productIdea, chat_input: chatInput}),
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

//Event-Listener für Patterns-Funktion
document.getElementById("patterns-examples-button").addEventListener("click", async () => {
  await getBusinessModelPatterns();
});

//What-If Stimuli: Sende eine Anfrage an GPT, What-If Fragen für die Produktidee zu nennen.
async function getWhatIf() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  let chatInput = document.getElementById("chat-input").value;
  const productIdea = localStorage.getItem("product-idea");
  const inputsData = {};

  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = "Give me What-If questions for my current Idea.";
  }

  console.log(inputsData);

  const response = await fetch("/get_what_if_stimuli", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({product_idea: productIdea, chat_input: chatInput}),
  });

  // API Antwort auswerten und dem Chatverlauf hinzufügen
  const data = await response.json();
  const whatIfResult = data.whatif_result;
  let formattedMessage = whatIfResult.replace(/\n/g, '<br>');

  // Ladekreis ausblenden
  document.getElementById("loading-circle-container").style.display = 'none';
  // Evaluation anzeigen
  const chatHistoryContainer = document.getElementById("chat-history");
  chatHistoryContainer.innerHTML += `<div class="user-message">User: ${chatInput}</div>`;
  chatHistoryContainer.innerHTML += `<div class="ai-message">ChatGPT: ${formattedMessage}</div>`;

}

//Event-Listener für What-If-Funktion
document.getElementById("whatif-button").addEventListener("click", async () => {
  await getWhatIf();
});


//Tippfunktion: Sende eine Anfrage an GPT, um für die Entwicklung des Business Model Canvas Tipps zu erhalten.
async function tipsBusinessModelCanvas() {
  // Ladekreis anzeigen
  document.getElementById("loading-circle-container").style.display = 'block';

  //Laden der Produktidee und der Building block details vom local storage und den Chat input vom Input Feld
  const productIdea = localStorage.getItem("product-idea");
  let chatInput = document.getElementById("chat-input").value;
  // Wenn der Chat Input leer ist, setze den Chat Input in einen Default-Wert
  if (!chatInput) {
    chatInput = `Give me tips for developing the Business Model Canvas.`;
  }
  // API Anfrage nach Tipps
  const response = await fetch("/tips_business_model_canvas", {
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

  const chatContainer = document.getElementById("chat-container");
}

//Event-Listener für Tipps
document.getElementById("tips-button").addEventListener("click", async () => {
  await tipsBusinessModelCanvas();
});

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

//Dropdown Canvas Template
function updateCanvasTemplate() {
  const canvasType = document.getElementById("canvas-select").value;

  const businessModelCanvasTitles = {
    "key-partners-title": "Key Partners",
    "key-activities-title": "Key Activities",
    "key-resources-title": "Key Resources",
    "value-propositions-title": "Value Propositions",
    "customer-segments-title": "Customer Segments",
    "customer-relationships-title": "Customer Relationships",
    "channels-title": "Channels",
    "cost-structure-title": "Cost Structure",
    "revenue-streams-title": "Revenue Streams",
  };

  const leanCanvasTitles = {
    "key-partners-title": "Problem",
    "key-activities-title": "Solution",
    "key-resources-title": "Key Metrics",
    "value-propositions-title": "Unique Value Proposition",
    "customer-segments-title": "Customer Segments",
    "customer-relationships-title": "Unfair Advantage",
    "channels-title": "Channels",
    "cost-structure-title": "Cost Structure",
    "revenue-streams-title": "Revenue Streams",
  };

  const environmentalCanvasTitles = {
    "key-partners-title": "Supplies and Out-sourcing",
    "key-activities-title": "Production",
    "key-resources-title": "Materials",
    "value-propositions-title": "Functional Value",
    "customer-segments-title": "Use Phase",
    "customer-relationships-title": "End-of-Life",
    "channels-title": "Distribution",
    "cost-structure-title": "Environmental Impacts",
    "revenue-streams-title": "Environmental Benefits",
  };

  const socialCanvasTitles = {
    "key-partners-title": "Local Communities",
    "key-activities-title": "Governance",
    "key-resources-title": "Employees",
    "value-propositions-title": "Social Value",
    "customer-segments-title": "End-User",
    "customer-relationships-title": "Societal Culture",
    "channels-title": "Scale Outreach",
    "cost-structure-title": "Social Impacts",
    "revenue-streams-title": "Social Benefits",
  };

  let buildingBlockTitles = {};

  switch (canvasType) {
    case "bmc":
      buildingBlockTitles = businessModelCanvasTitles;
      break;
    case "lean":
      buildingBlockTitles = leanCanvasTitles;
      break;
    case "environmental":
      buildingBlockTitles = environmentalCanvasTitles;
      break;
    case "social":
      buildingBlockTitles = socialCanvasTitles;
      break;
    default:
      buildingBlockTitles = businessModelCanvasTitles;
  }

  //  Schleige durch die Building blocks zum Updaten der Titel
  for (const id in buildingBlockTitles) {
    const buildingBlock = document.getElementById(id);
    if (buildingBlock) {
      buildingBlock.innerText = buildingBlockTitles[id];
      localStorage.setItem(id, buildingBlockTitles[id]); // Titel im Local Storage speichern
    }
  }
}

// Export to PNG, welches Pre-Elemente benutzt, damit Textareas richtig angezeigt werden und nicht nach 1 Zeile abgeschnitten werden
document.getElementById("export-button").addEventListener("click", function () {
  const element = document.getElementById("main-content");

  // Verstecke die Help und Notes Area
  const helpContainer = document.getElementById("help-container");
  const noteContainer = document.getElementById("note-container");
  helpContainer.style.display = "none";
  noteContainer.style.display = "none";
  
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
    scale: 3,
    width: element.offsetWidth,
    height: element.offsetHeight,
    scrollY: 0,
    scrollX: 0,
    backgroundColor: null,
  };

  // Speicher den Canvas für den User
  html2canvas(element, opt).then(function (canvas) {
    //Ersetze die Pre Elements mit den originalen Textareas, setze die Help und Notes Area wieder auf sichtbar
    preElements.forEach((pre, index) => {
      pre.parentNode.replaceChild(textareas[index], pre);
    });
    helpContainer.style.display = "block";
    noteContainer.style.display = "block";

    const link = document.createElement("a");
    link.download = "mycanvas.png";
    link.href = canvas.toDataURL();
    link.click();
  });
});

// Exportiere die Local-Storage Session Daten in eine JSON File
function exportLocalStorage() {
  const data = JSON.stringify(localStorage);
  const blob = new Blob([data], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const fileName = window.prompt("Enter a file name for the export", "localStorageData");
  const formattedFileName = fileName + ".json";
  if (fileName) {
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}



//Importiere Session-Daten aus einer JSON File
function importLocalStorage() {
  try {
    if (!window.FileReader) {
      throw new Error("Browser not supported.");
    }
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json";
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (!file) {
        throw new Error("No file selected.");
      }
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const data = JSON.parse(reader.result);
          if (!data) {
            throw new Error("Invalid file format.");
          }
          Object.keys(data).forEach((key) => {
            localStorage.setItem(key, data[key]);
          });
          alert("Import successful!");
        } catch (error) {
          alert(`Import failed: ${error.message}`);
        }
      };
      reader.readAsText(file);
    });
    input.click();
  } catch (error) {
    alert(`Import failed: ${error.message}`);
  }
}


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
    localStorage.setItem("notes", noteText);
  }
}

function loadNotesFromLocalStorage() {
  const savedNotes = localStorage.getItem("notes");
  if (savedNotes) {
    document.getElementById("note-text").value = savedNotes;
  }
}

// Eventlistener der die Notizen beim Laden der Seite aus dem Local Storage lädt 
window.addEventListener("load", loadNotesFromLocalStorage);


//Help-Fenster
function toggleHelpWindow() {
  const helpContainer = document.getElementById("help-container");
  if (helpContainer.style.bottom === "20px") {
    helpContainer.style.bottom = "-600px";
  } else {
    helpContainer.style.bottom = "20px";
  }
}
