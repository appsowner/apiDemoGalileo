import os
import time
from flask import Flask, request, jsonify
from galileo import openai, logger  # Las importaciones originales
from dotenv import load_dotenv

load_dotenv()

# Inicializa el cliente OpenAI con trazado automático
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
)

# Inicializa GalileoLogger manualmente
galileo_logger = logger.GalileoLogger(project="flask-geography", log_stream="flask-api")

app = Flask(__name__)


@app.route('/')
def health_check():
    return jsonify({"status": "API is running"})


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
     
    
    system_prompt = data.get('system_prompt', "You are a helpful assistant that answers succinctly.")  # valor por defecto
    user_prompt = data.get('prompt')
    output_prompt= data.get('output_prompt')
    model_prompt =data.get('model_prompt')
    print('model_prompt')
    print(model_prompt)
    print('system prompt')
    print(system_prompt)
    print('user_prompt ')
    print(user_prompt)
    print('output_prompt')
    print(output_prompt)
   

    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    full_input = f"System: {system_prompt}\nUser: {user_prompt}"
    trace = galileo_logger.start_trace(input=full_input)

    start_time = time.time_ns()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    end_time = time.time_ns()

    output = response.choices[0].message.content.strip()
    print(response)
    print("Prompt tokens:", getattr(response.usage, "prompt_tokens", None))
    print("Completion tokens:", getattr(response.usage, "completion_tokens", None))
    print("Total tokens:", getattr(response.usage, "total_tokens", None))

    input_tkn=getattr(response.usage, "prompt_tokens", None)
    completion_tkn=getattr(response.usage, "completion_tokens", None)
    total_tkn= getattr(response.usage, "total_tokens", None)

    print("Prompt tokens:", input_tkn)
    print("Completion tokens:", completion_tkn)
    print("Total tokens:", total_tkn)


    final_output = output_prompt if output_prompt else output

    print(" final_output:",  final_output)

    galileo_logger.add_llm_span(
        input=full_input,
        output=final_output,
        model=model_prompt,
        duration_ns=end_time - start_time,
        num_input_tokens=input_tkn,
        num_output_tokens=completion_tkn,
        total_tokens= total_tkn
    )

    galileo_logger.conclude(output=output)
    galileo_logger.flush()

    return jsonify({"response": output})

@app.route('/generate2', methods=['POST'])
def generate2():
    data = request.get_json()
    
    system_prompt = data.get('system_prompt', "You are a helpful assistant that answers succinctly.")
    user_prompt = data.get('prompt')
    output_prompt = data.get('output_prompt')
    model_prompt = data.get('model_prompt', "gpt-4o")
    
    print('model_prompt:', model_prompt)
    print('system prompt:', system_prompt)
    print('user_prompt:', user_prompt)
    print('output_prompt:', output_prompt)
   
    # Preparar mensajes para OpenAI
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    # ESTRATEGIA 1: Input completo para análisis de Galileo
    # Incluir system prompt en el input para que Galileo pueda analizarlo
    full_context_input = f"""SYSTEM INSTRUCTIONS: {system_prompt}

USER QUERY: {user_prompt}"""
    
    # ESTRATEGIA 2: Crear un input estructurado para mejor análisis
    structured_input = {
        "system_role": system_prompt,
        "user_query": user_prompt,
        "expected_behavior": "Follow system instructions while answering user query"
    }
    
    # Usar la estrategia 1 (más simple y efectiva)
    galileo_input = full_context_input
    
    # Iniciar trace en Galileo
    trace = galileo_logger.start_trace(input=galileo_input)
    
    start_time = time.time_ns()
    
    try:
        # Llamada a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        
        end_time = time.time_ns()
        
        # Extraer respuesta y métricas
        actual_output = response.choices[0].message.content.strip()
        input_tkn = getattr(response.usage, "prompt_tokens", 0)
        completion_tkn = getattr(response.usage, "completion_tokens", 0)
        total_tkn = getattr(response.usage, "total_tokens", 0)
        
        print("Response:", response)
        print("Prompt tokens:", input_tkn)
        print("Completion tokens:", completion_tkn)
        print("Total tokens:", total_tkn)
        
        # ESTRATEGIA 3: Output estructurado para mejor análisis
        # Si tienes un output_prompt personalizado, inclúyelo en el análisis
        if output_prompt:
            # Galileo analizará tanto la respuesta real como la esperada
            analysis_output = f"""ACTUAL MODEL RESPONSE: {actual_output}

EXPECTED/CUSTOM RESPONSE: {output_prompt}

ANALYSIS NOTE: Compare actual response adherence to system instructions and alignment with expected output."""
            final_output = analysis_output
        else:
            final_output = actual_output
        
        print("Final output for Galileo:", final_output)
        
        # ESTRATEGIA 4: Metadata rica para análisis adicional
        metadata = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "actual_model_output": actual_output,
            "custom_expected_output": output_prompt,
            "analysis_type": "system_prompt_adherence",
            "model_configuration": model_prompt
        }
        
        # Registrar en Galileo con contexto completo
        galileo_logger.add_llm_span(
            input=galileo_input,  # Incluye system + user prompt
            output=final_output,  # Incluye análisis completo
            model=model_prompt,
            duration_ns=end_time - start_time,
            num_input_tokens=input_tkn,
            num_output_tokens=completion_tkn,
            total_tokens=total_tkn,
            metadata=metadata  # Metadata rica para análisis
        )
        
        # Concluir el trace
        galileo_logger.conclude(output=final_output)
        galileo_logger.flush()
        
        return jsonify({
            "response": actual_output,  # Retornar la respuesta real del modelo
            "analysis": {
                "system_prompt_included": True,
                "custom_output_provided": bool(output_prompt),
                "galileo_tracking": "full_context"
            },
            "tokens_used": {
                "input": input_tkn,
                "output": completion_tkn,
                "total": total_tkn
            }
        })
        
    except Exception as e:
        print(f"Error in generate endpoint: {str(e)}")
        galileo_logger.conclude(output=f"Error: {str(e)}")
        galileo_logger.flush()
        
        return jsonify({
            "error": str(e)
        }), 500


# ALTERNATIVA: Función para análisis post-procesamiento
def analyze_response_quality(system_prompt, user_prompt, actual_output, expected_output=None):
    """
    Función auxiliar para crear un análisis estructurado
    que Galileo puede usar para evaluaciones más profundas
    """
    analysis = {
        "context": {
            "system_instructions": system_prompt,
            "user_request": user_prompt
        },
        "response": {
            "actual": actual_output,
            "expected": expected_output
        },
        "evaluation_criteria": [
            "System prompt adherence",
            "User query relevance", 
            "Response quality",
            "Instruction following"
        ]
    }
    
    return analysis


# ESTRATEGIA 5: Endpoint específico para análisis de calidad
@app.route('/analyze_quality', methods=['POST'])
def analyze_quality():
    """
    Endpoint dedicado para análisis de calidad con Galileo
    """
    data = request.get_json()
    
    system_prompt = data.get('system_prompt')
    user_prompt = data.get('user_prompt') 
    actual_output = data.get('actual_output')
    expected_output = data.get('expected_output')
    
    # Input para análisis de calidad
    quality_input = f"""EVALUATE RESPONSE QUALITY:

SYSTEM INSTRUCTIONS: {system_prompt}

USER QUERY: {user_prompt}

ACTUAL RESPONSE: {actual_output}

EXPECTED RESPONSE: {expected_output if expected_output else 'Not specified'}

EVALUATION TASK: Analyze if the actual response follows system instructions and appropriately answers the user query."""
    
    # En este caso, el "output" sería tu evaluación o simplemente confirmar que se debe analizar
    quality_output = "Response submitted for quality analysis"
    
    trace = galileo_logger.start_trace(input=quality_input)
    
    galileo_logger.add_llm_span(
        input=quality_input,
        output=quality_output,
        model="quality_analysis",
        metadata={
            "analysis_type": "response_quality_evaluation",
            "has_expected_output": bool(expected_output)
        }
    )
    
    galileo_logger.conclude(output=quality_output)
    galileo_logger.flush()
    
    return jsonify({"status": "Analysis submitted to Galileo"})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
