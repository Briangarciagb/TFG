from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from auth import autorizar as google_autorizar, oauth2callback, get_credentials
from calendar_api import agregar_evento
from fitness import get_fitness_data, get_sleep_data
from googleapiclient.discovery import build
from datetime import datetime
import os

# Configuración de la aplicación Flask
app = Flask(__name__, template_folder='../templates')
app.secret_key = "clave_secreta_segura"
CORS(app)

# Rutas de la aplicación
@app.route('/')
def principal():
    return render_template('Principal.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness.html')

@app.route('/alimentacion')
def alimentacion():
    return render_template('alimentacion.html')

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

@app.route('/agregar_evento', methods=['POST'])
def evento():
    return agregar_evento()

@app.route('/autorizar')
def autorizar():
    return google_autorizar()

@app.route('/oauth2callback')
def callback():
    return oauth2callback()

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

        # Aquí actualizamos las claves para que coincidan con las esperadas por el frontend
        return jsonify({
            "status": "success",
            "data": {
                "pasos": fitness_data.get("steps", 0),
                "calorias": fitness_data.get("calories", 0),
                "distancia": fitness_data.get("distance", 0),
                "sueno": sleep_data.get("sleep", 0)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/ver_credenciales')
def ver_credenciales():
    if 'credentials' in session:
        return jsonify(session['credentials'])
    return jsonify({"error": "No se encontraron credenciales."})

# Inicio de la aplicación
if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)
