# app.py
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
openai.api_key = "TU_API_KEY_AQUÍ"  # o usa variable de entorno

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    # Llama a la API de OpenAI:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content": user_message}]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)}), 500
