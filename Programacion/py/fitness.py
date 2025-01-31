from flask import Flask, request, jsonify
from auth import get_credentials  # Importa la función para obtener las credenciales
from googleapiclient.discovery import build
from datetime import datetime

# Define funciones de fitness
def get_fitness_data(service, fecha):
    try:
        # Llamada simulada a la API de Google Fit
        # En la implementación real, se deben usar los endpoints adecuados
        return {"steps": 1000, "calories": 200, "distance": 1.5}
    except Exception as e:
        return {"error": str(e)}

def get_sleep_data(service, fecha):
    try:
        # Llamada simulada a la API de Google Fit
        return {"sleep": 7}
    except Exception as e:
        return {"error": str(e)}

app = Flask(__name__)

@app.route('/datos', methods=['POST'])
def obtener_datos():
    try:
        data = request.get_json()
        fecha_str = data.get("fecha")
        if not fecha_str:
            return jsonify({"status": "error", "message": "Fecha no proporcionada."}), 400
        
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        creds = get_credentials()
        if not creds:
            return jsonify({"status": "error", "message": "No autorizado"}), 401

        service = build("fitness", "v1", credentials=creds)
        fitness_data = get_fitness_data(service, fecha)
        sleep_data = get_sleep_data(service, fecha)

        return jsonify({
            "status": "success",
            "data": {
                "steps": fitness_data.get("steps", 0),
                "calories": fitness_data.get("calories", 0),
                "distance": fitness_data.get("distance", 0),
                "sleep": sleep_data.get("sleep", 0)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)