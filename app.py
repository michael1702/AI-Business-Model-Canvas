import os
import openai
from flask import Flask, jsonify, redirect, render_template, request, url_for, json
import requests
from dotenv import load_dotenv

# Lade environment variables
load_dotenv()

app = Flask(__name__)
client = openai.OpenAI()


def llm(messages, *, model="gpt-5-mini", max_tokens=2000):
    """
    - json_mode=True erzwingt strikt gültiges JSON via Responses-API.
    - max_tokens erhöht, damit das Modell nicht in der Mitte abbricht.
    """
    args = {
        "model": model,
        "input": messages,
        "max_output_tokens": max_tokens,
    }

    resp = client.responses.create(**args)

    # bevorzugt: SDK-Shortcut
    txt = getattr(resp, "output_text", None)
    if txt:
        return txt.strip()

# Main index route
@app.route("/")
def index():
    return render_template("index.html")



# Route: Chat mit GPT
@app.route("/chat_with_gpt4", methods=["POST"])
def chat_with_gpt4():
    messages = request.json["messages"]
    new_message = request.json["new_message"]
    messages = list(messages) + [{"role": "user", "content": new_message}]

    #API-Call
    reply = llm(messages, model="gpt-5-mini", max_tokens=500)
    #return JSON-File of reply
    return jsonify({"reply": reply})



@app.route('/example_canvas_by_product', methods=["POST"])
def example_canvas():
    product_idea = request.json["product_idea"]
    prompt = f'''Your role: An AI Business Model Development Assistant.
    Task: I am Building a Business Model Canvas. Provide an example of the building blocks for said product idea as a JSON object. Example Input product Idea: Bakery. Example output:
    {{
    "key-partners": "-Local farmers\n-suppliers\n-distributors",
    "key-activities": -Baking\n-packaging\n-distributing products",
    "key-resources": "-Equipment\n-ingredients\n-staff\n-delivery vehicles",
    "value-propositions": "-Fresh\n-quality ingredients\n-unique flavor combinations\n-convenience",
    "customer-relationships": "-Personalized customer service \n-loyalty programs",
    "channels": "-Retail stores\n-online ordering\n-delivery services",
    "customer-segments": "-Local residents\n-tourists\n-businesses",
    "cost-structure": "-Ingredients\n-labor\n-equipment\n-delivery costs",
    "revenue-streams": "-Retail sales\n-online orders\n-delivery fees"
    }}
    Input: The Product Idea: {product_idea} \n Output:'''


    output = llm([{"role": "user", "content": prompt}], max_tokens=2000)
    start = output.find("{")
    if start == -1:
        return jsonify({"error": "Kein JSON im Modell-Output gefunden.", "raw": output}), 502
    return jsonify(json.loads(output[start:]))

#Route um einen gegebenen Building Block ausgefüllt zu bekommen, abhängig von der Produktidee
@app.route('/prefill_building_block', methods=["POST"])
def prefill_building_block():

    product_idea = request.json["product_idea"]
    building_block= request.json["building_block"]
    #Prompt gibt die Syntax der JSON. Dabei doppelte geschweifte klammern, sodass die Struktur richtig an die AI gesendet wird
    prompt = f'''Your role: An AI Business Model Development Assistant.
    Task: I am Building a Business Model Canvas. Provide an example of the building block I tell you for said product idea as a JSON object. Example Input product Idea: Bakery. Example Building block: Value Propositions Example output: 
    {{
    "value-propositions": "-Fresh\\n-Quality ingredients\\n-Unique flavor combinations\\n-Convenience"
    }}
     Input: The Product Idea: {product_idea}  \\n The Building Block: {building_block} \\n
     Output:'''    

    # Ausführen der API Request und Vorbereitung der JSON-Antwort
    output = llm([{"role": "user", "content": prompt}], max_tokens=1000)
    output_index = output.index("{")
    output_formatted = output[output_index:]

    return jsonify(json.loads(output_formatted))  # Return die JSON Antwort


#Route um ein Example Value Proposition Canvas für eine gegebene Produktidee, Value Proposition und Customer Segments zu erhalten.
@app.route('/exampleVPC', methods=["POST"])
def example_value_proposition_canvas():
    product_idea = request.json["productIdea"]
    value_propositions = request.json["valuePropositions"]
    customer_segments = request.json["customerSegments"]

    prompt = f''' Your role: An AI Business Model Development Assistant.
Task:Create a Value Proposition Canvas for a product idea, with the provided Value Propositions and Customer Segments from a Business Model Canvas.i need to improve the Value Proposition and the Customer segments and create a match between the customer needs and my value offering. The Pain relievers should fit the pains and the gain creators should fit the needed gains of a customer. It can be an expected gain or an unexpected gain. Provide a JSON Object consisting of the Value Proposition Canvas fields. 
Example input:
"Product Idea": "bakery", 
"value-proposition": "Fresh, quality ingredients, unique flavor combinations and convenience",
"customer-segments": "Local residents, tourists, and businesses"

Example Output:
 {{
"products-services": "-Project management software with customizable features \\n-Real-time collaboration tools \\n-Task assignment and tracking \\n-Analytics and reporting",
"gain-creators": "-Efficient project management that saves time and resources \\n-Real-time collaboration that improves communication and productivity \\n-Customizable features that fit the unique needs of each team or project \\n-Analytics and reporting that provide insights for better decision-making",
"pain-relievers": "-Eliminates the need for manual tracking and reporting \\n-Reduces miscommunication and delays \\n-Offers flexibility to adapt to changing project requirements",
"customer-jobs": "-Manage and track project progress \\n-Collaborate with team members and stakeholders \\n-Customize features to fit specific project needs \\n-Analyze and report on project data",
"gains": "-Efficient project management that saves time and resources \\n-Improved communication and collaboration \\n-Customizable features that fit specific project needs \\n-Insights and analytics for better decision-making",
"pains": "-Manual tracking and reporting \\n-Miscommunication and delays \\n-Lack of flexibility to adapt to changing project requirements"
}}


    Product Idea: {product_idea},
    Value Propositions: {value_propositions},
    Customer Segments: {customer_segments},
    Output as JSON:'''

    output = llm([{"role": "user", "content": prompt}], max_tokens=2000)
    output_index = output.index("{")

    output_formatted = output[output_index:]
    return jsonify(json.loads(output_formatted))

#Route für die Correctness Checker Funktion im BMC
@app.route("/check_correctness", methods=["POST"])
def check_correctness():
    # Extrahiere die Inputs der eingehenden Anfrage
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n  The inputs for the building blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}. '''
    message += '''\\nWork as a correctness checker. Check for syntax and semantic mistakes and general mistakes at filling out the canvas. Also check if the inputs fit to their building block. Correctness check:'''

    check_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Ergebnis als JSON-Objekt
    return jsonify({"check_result": check_result})

#Route für die Correctness Checker Funktion im VPC
@app.route("/check_correctness_vpc", methods=["POST"])
def check_correctness_vpc():
    # Extrahiere die Inputs der eingehenden Anfrage
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. 
    Also remember there should be the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea}. \\n  The inputs for the canvas blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}. '''
    message += '''\\nWork as a correctness checker. Check for syntax and semantic mistakes and general mistakes at filling out the canvas. Also check if the inputs fit to their building block. Correctness check:'''
    
    check_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Ergebnis als JSON-Objekt
    return jsonify({"check_result": check_result})

#Route für die inhaltliche Evaluierfunktion
@app.route("/evaluate_all_inputs", methods=["POST"])
def evaluate_all_inputs():
    # Extrahiere die Inputs der eingehenden Anfrage
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n  The inputs for the building blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''

    evaluation_result = llm([{"role": "user", "content": message}], max_tokens=1000)

    # Return das Ergebnis als JSON-Objekt
    return jsonify({"evaluation_result": evaluation_result})


#Route für die inhaltliche Evaluierfunktion auf VPC Ebene
@app.route("/evaluate_vpc", methods=["POST"])
def evaluate_vpc():
    # Extrahiere die Inputs der eingehenden Anfrage
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. 
    Also remember there should be the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea}. \\n  The inputs for the canvas blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''

    evaluation_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Ergebnis als JSON-Objekt
    return jsonify({"evaluation_result": evaluation_result})


# Route für die Evaluierfunktion auf Building Block Ebene
@app.route("/evaluate_building_block", methods=["POST"])
def evaluate_building_block():

    product_idea = request.json["product_idea"]
    building_block = request.json["building_block"]
    building_block_input = request.json["building_block_input"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n The building block: {building_block} \\n The Idea for the Building block: {building_block_input}  \\n chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''
    evaluation_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Ergebnis als JSON-Objekt
    return jsonify({"evaluation_result": evaluation_result})

#Route für die Business Model Patterns Funktion
@app.route("/get_business_model_patterns", methods=["POST"])
def get_business_model_patterns():
    # Extrahiere die Inputs der eingehenden Anfrage
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n chat input: {chat_input}  \\n I want to be more creative in building my BMC and need Business Model Patterns for it. Give me relevant Business Model Patterns for my use case. Output:'''

    evaluation_result = llm([{"role": "user", "content": message}], max_tokens=1000)

    # Return das Ergebnis als JSON-Objekt
    return jsonify({"evaluation_result": evaluation_result})

#Route um What-If Stimuli für eine gegebene Produktidee zu erhalten
@app.route("/get_what_if_stimuli", methods=["POST"])
def get_what_if_stimuli():
    # Extrahiere die Inputs der eingehenden Anfrage
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Vorbereiten der message für GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. I want to be more creative in building my BMC and need What-If questions for it. Give me relevant What-If questions for my use case. 
    “What if” questions help us break free of constraints imposed by current models. They should provoke us and challenge our thinking. They should disturb us as intriguing, difficult-to-execute propositions. 
    Example What-if-questions: 
    1. What if furniture buyers picked up components in flat pack form from a large warehouse and assembled the products themselves in their homes? What is common practice today was unthinkable until IKEA introduced the concept in the 1960s.
    2. What if car manufacturers didn’t sell cars, but provided mobility services? In 2008 Daimler launched car2go, an experimental business in the German city of Ulm. Car2go’s fleet of vehicles allows users to pick up and drop off cars anywhere in the city, paying by-the-minute fees for mobility services.
    3. What if voice calls were free worldwide? In 2003 Skype launched a service that allowed free voice calling via the Internet. After five years Skype had acquired 400 million registered users who collectively had made 100 billion free calls.
    The Product Idea: {product_idea}. \\n chat input: {chat_input}  \\nOutput:'''

    whatif_result = llm([{"role": "user", "content": message}], max_tokens=1000)

    # Return das Ergebnis als JSON-Objekt
    return jsonify({"whatif_result": whatif_result})

# Route um Tips für die Entwicklung des BMC zu erhalten
@app.route("/tips_business_model_canvas", methods=["POST"])
def tips_business_model_canvas():

    product_idea = request.json["product_idea"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n chat input: {chat_input}  \\n Instruction: Mention the Value Proposition Canvas, a subsite on the webApp \\n What tips do you have for developing the Business Model Canvas? What are the steps I should take? Tips:'''
    tips_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Tipps-Ergebnis als JSON-Objekt
    return jsonify({"tips_result": tips_result})

# Route um Tipps im derzeitigen Building Block zu erhalten
@app.route("/tips_building_block", methods=["POST"])
def tips_building_block():
    # Extrahiere die Produktidee und Building Block Details aus der eingehenden Anfrage
    product_idea = request.json["product_idea"]
    building_block = request.json["building_block"]
    building_block_input = request.json["building_block_input"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n The building block: {building_block} \\n The Idea for the Building block: {building_block_input}  \\n chat input: {chat_input}  \\n What tips do you have for filling in this building block? What are the steps I should take? Tips:'''
    tips_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Tipps-Ergebnis als JSON-Objekt
    return jsonify({"tips_result": tips_result})


# Route um Tipps beim VPC zu erhalten
@app.route("/tips_VPC", methods=["POST"])
def tips_value_proposition_canvas():

    product_idea = request.json["product_idea"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. Also explain about the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea} chat input: {chat_input}  \\n What tips do you have for developing the Value Proposition Canvas? What steps should I take? Tips:'''
    tips_result = llm([{"role": "user", "content": message}], max_tokens=1000)
    # Return das Tipps-Ergebnis als JSON-Objekt
    return jsonify({"tips_result": tips_result})

#Route für die process page
@app.route('/process')
def process():
    return render_template('process.html')

#Route für die key partners page
@app.route('/key-partners')
def key_partners():
    return render_template('buildingblocks/key-partners.html')

#Route für die key activities page
@app.route('/key-activities')
def key_activities():
    return render_template('buildingblocks/key-activities.html')

##Route für die key resources page
@app.route('/key-resources')
def key_resources():
    return render_template('buildingblocks/key-resources.html')

##Route für die value proposition page
@app.route('/value-propositions')
def value_proposition():
    return render_template('/buildingblocks/value-propositions.html')

#Route für die customer segments page
@app.route('/customer-segments')
def customer_segments():
    return render_template('buildingblocks/customer-segments.html')

#Route für die customer relationships page
@app.route('/customer-relationships')
def customer_relationships():
    return render_template('buildingblocks/customer-relationships.html')

#Route für die channels page
@app.route('/channels')
def channels():
    return render_template('buildingblocks/channels.html')

#Route für die cost structure page
@app.route('/cost-structure')
def cost_structure():
    return render_template('buildingblocks/cost-structure.html')

#Route für die revenue streams page
@app.route('/revenue-streams')
def revenue_streams():
    return render_template('buildingblocks/revenue-streams.html')

#Route für die the value proposition canvas
@app.route('/value-proposition-canvas')
def value_proposition_canvas():
    return render_template('value-proposition-canvas.html')


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8888)),host='0.0.0.0',debug=True)
