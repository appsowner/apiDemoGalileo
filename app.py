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


    galileo_logger.add_llm_span(
        input=full_input,
        output=output,
        model="gpt-4o",
        duration_ns=end_time - start_time,
        num_input_tokens=input_tkn,
        num_output_tokens=completion_tkn,
        total_tokens= total_tkn
    )

    galileo_logger.conclude(output=output)
    galileo_logger.flush()

    return jsonify({"response": output})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
