from flask import Blueprint, request, jsonify, current_app
import json

api= Blueprint("api",   __name__, url_prefix="/api/v1")

@api.get("/health")
def health(): return jsonify({"status":"ok"})


# Ruta: Chat con GPT
@api.post("/chat_with_gpt5")
def chat_with_gpt5():
    messages = request.json["messages"]
    new_message = request.json["new_message"]
    messages = list(messages) + [{"role": "user", "content": new_message}]

    # Llamada a la API
    reply = current_app.config["LLM"].respond(messages,model="gpt-5-mini", max_tokens=500)
    # devolver archivo JSON con la respuesta
    return jsonify({"reply": reply})

@api.post("/bmc/example")
def example_canvas():
    current_app.logger.info({"evt":"api_in","route":"/bmc/example","json":request.get_json()})
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

    output = current_app.config["LLM"].respond(
        [{"role":"user","content": prompt}],
        model="gpt-5-mini", max_tokens=2000
    )
    start = output.find("{")
    if start == -1:
        return jsonify({"error":"No JSON","raw": output}), 502
    return jsonify(json.loads(output[start:]))

# Ruta para rellenar un Bloque de Construcción dado, dependiendo de la idea de producto
@api.post("/bmc/prefill_building_block")
def prefill_building_block():
    product_idea = request.json["product_idea"]
    building_block = request.json["building_block"]
    # El prompt define la sintaxis del JSON. Doble llave para que la estructura se envíe correctamente a la IA
    prompt = f'''Your role: An AI Business Model Development Assistant.
    Task: I am Building a Business Model Canvas. Provide an example of the building block I tell you for said product idea as a JSON object. Example Input product Idea: Bakery. Example Building block: Value Propositions Example output: 
    {{
    "value-propositions": "-Fresh\\n-Quality ingredients\\n-Unique flavor combinations\\n-Convenience"
    }}
     Input: The Product Idea: {product_idea}  \\n The Building Block: {building_block} \\n
     Output:'''    

    # Ejecutar la petición a la API y preparar la respuesta JSON
    output = current_app.config["LLM"].respond(
        [{"role":"user","content": prompt}],
        model="gpt-5-mini", max_tokens=1000
    )
    return jsonify(json.loads(output[output.index("{"):]))  # Devolver la respuesta JSON


# Ruta para obtener un ejemplo de Value Proposition Canvas para una idea de producto dada, Value Proposition y Customer Segments.
@api.post('/vpc/exampleVPC')
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

    output = current_app.config["LLM"].respond(
        [{"role":"user","content": prompt}],
        model="gpt-5-mini", max_tokens=2000
    )
    output_index = output.index("{")

    output_formatted = output[output_index:]
    return jsonify(json.loads(output_formatted))


# Ruta para la función Correctness Checker en el BMC
@api.post("/bmc/check_correctness")
def check_correctness():
    # Extraer las entradas de la petición entrante
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n  The inputs for the building blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}. '''
    message += '''\\nWork as a correctness checker. Check for syntax and semantic mistakes and general mistakes at filling out the canvas. Also check if the inputs fit to their building block. Correctness check:'''

    check_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    )
    # Devolver el resultado como objeto JSON
    return jsonify({"check_result": check_result})


# Ruta para la función Correctness Checker en el VPC
@api.post("/vpc/check_correctness")
def check_correctness_vpc():
    # Extraer las entradas de la petición entrante
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. 
    Also remember there should be the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea}. \\n  The inputs for the canvas blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}. '''
    message += '''\\nWork as a correctness checker. Check for syntax and semantic mistakes and general mistakes at filling out the canvas. Also check if the inputs fit to their building block. Correctness check:'''
    
    check_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    )    
    # Devolver el resultado como objeto JSON
    return jsonify({"check_result": check_result})


# Ruta para la función de evaluación de contenido
@api.post("/bmc/evaluate")
def evaluate():
    # Extraer las entradas de la petición entrante
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n  The inputs for the building blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''

    evaluation_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    ) 

    # Devolver el resultado como objeto JSON
    return jsonify({"evaluation_result": evaluation_result})


# Ruta para la función de evaluación de contenido a nivel VPC
@api.post("/vpc/evaluate")
def evaluate_vpc():
    # Extraer las entradas de la petición entrante
    inputs_data = request.json["inputs_data"]
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. 
    Also remember there should be the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea}. \\n  The inputs for the canvas blocks are: \\n'''
    for block, input_value in inputs_data.items():
        message += f'''{block}: {input_value} \\n'''
    message += f'''chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''

    evaluation_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    ) 
    # Devolver el resultado como objeto JSON
    return jsonify({"evaluation_result": evaluation_result})


# Ruta para la función de evaluación a nivel de Bloque de Construcción
@api.post("/evaluate_building_block")
def evaluate_building_block():

    product_idea = request.json["product_idea"]
    building_block = request.json["building_block"]
    building_block_input = request.json["building_block_input"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n The building block: {building_block} \\n The Idea for the Building block: {building_block_input}  \\n chat input: {chat_input}  \\n Give me Feedback. Would you recommend alternatives? Evaluation:'''
    evaluation_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    ) 
    # Devolver el resultado como objeto JSON
    return jsonify({"evaluation_result": evaluation_result})

# Ruta para la función Business Model Patterns
@api.post("/bmc/patterns")
def get_business_model_patterns():
    # Extraer las entradas de la petición entrante
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea}. \\n chat input: {chat_input}  \\n I want to be more creative in building my BMC and need Business Model Patterns for it. Give me relevant Business Model Patterns for my use case. Output:'''

    evaluation_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    ) 

    # Devolver el resultado como objeto JSON
    return jsonify({"evaluation_result": evaluation_result})

# Ruta para obtener estímulos "What-If" para una idea de producto dada
@api.post("/bmc/what_if")
def get_what_if_stimuli():
    # Extraer las entradas de la petición entrante
    chat_input = request.json["chat_input"]
    product_idea = request.json["product_idea"]

    # Preparar el mensaje para GPT
    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. I want to be more creative in building my BMC and need What-If questions for it. Give me relevant What-If questions for my use case. 
    “What if” questions help us break free of constraints imposed by current models. They should provoke us and challenge our thinking. They should disturb us as intriguing, difficult-to-execute propositions. 
    Example What-if-questions: 
    1. What if furniture buyers picked up components in flat pack form from a large warehouse and assembled the products themselves in their homes? What is common practice today was unthinkable until IKEA introduced the concept in the 1960s.
    2. What if car manufacturers didn’t sell cars, but provided mobility services? In 2008 Daimler launched car2go, an experimental business in the German city of Ulm. Car2go’s fleet of vehicles allows users to pick up and drop off cars anywhere in the city, paying by-the-minute fees for mobility services.
    3. What if voice calls were free worldwide? In 2003 Skype launched a service that allowed free voice calling via the Internet. After five years Skype had acquired 400 million registered users who collectively had made 100 billion free calls.
    The Product Idea: {product_idea}. \\n chat input: {chat_input}  \\nOutput:'''

    whatif_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    ) 

    # Devolver el resultado como objeto JSON
    return jsonify({"whatif_result": whatif_result})

# Ruta para obtener consejos para desarrollar el BMC
@api.post("/bmc/tips")
def tips_business_model_canvas():

    product_idea = request.json["product_idea"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n chat input: {chat_input}  \\n Instruction: Mention the Value Proposition Canvas, a subsite on the webApp \\n What tips do you have for developing the Business Model Canvas? What are the steps I should take? Tips:'''
    tips_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    )  
    # Devolver el resultado de consejos como objeto JSON
    return jsonify({"tips_result": tips_result})

# Ruta para obtener consejos para el Bloque de Construcción actual
@api.post("/tips_building_block")
def tips_building_block():
    # Extraer la idea de producto y los detalles del Bloque de Construcción de la petición entrante
    product_idea = request.json["product_idea"]
    building_block = request.json["building_block"]
    building_block_input = request.json["building_block_input"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Business Model Canvas. The Product Idea: {product_idea} \\n The building block: {building_block} \\n The Idea for the Building block: {building_block_input}  \\n chat input: {chat_input}  \\n What tips do you have for filling in this building block? What are the steps I should take? Tips:'''
    tips_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    )  
    # Devolver el resultado de consejos como objeto JSON
    return jsonify({"tips_result": tips_result})


# Ruta para obtener consejos para el VPC
@api.post("/vpc/tips")
def tips_value_proposition_canvas():

    product_idea = request.json["product_idea"]
    chat_input = request.json["chat_input"]

    message = f'''Your role: An AI Business Model Development Assistant.
    Task:I'm Building a Value Proposition Canvas as proposed from Osterwalder and Pigneur which makes a Customer Profile and a Value Proposition in order to to improve the Value Proposition and the Customer segments of a Business Model Canvas and create a match between the customer needs and my value offering. Also explain about the fit-phase where you match the pains and gains with the pain relievers and gain creators. The Product Idea: {product_idea} chat input: {chat_input}  \\n What tips do you have for developing the Value Proposition Canvas? What steps should I take? Tips:'''
    tips_result = current_app.config["LLM"].respond(
        [{"role":"user","content": message}],
        model="gpt-5-mini", max_tokens=1000
    )  
    # Devolver el resultado de consejos como objeto JSON
    return jsonify({"tips_result": tips_result})