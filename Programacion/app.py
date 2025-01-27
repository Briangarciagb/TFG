from flask import Flask, jsonify, render_template
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import json

app = Flask(__name__)
CORS(app)

# Configura los scopes necesarios para Google Fitness API
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def get_credentials():
    creds = None
    # Verifica si ya existe un token guardado
    if os.path.exists('token.json'):
        try:
            with open('token.json', 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
        except Exception as e:
            print(f"Error leyendo token: {e}")
    
    # Si no hay credenciales válidas, solicita autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refrescando token: {e}")
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credenciales.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Guarda las credenciales para la próxima vez
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error en el flujo de autorización: {e}")
    return creds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/conectar')
def conectar():
    try:
        creds = get_credentials()
        if creds and creds.valid:
            return jsonify({"status": "success", "message": "Conexión exitosa"})
        return jsonify({"status": "error", "message": "No se pudo obtener credenciales válidas"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/datos')
def obtener_datos():
    try:
        creds = get_credentials()
        if not creds or not creds.valid:
            return jsonify({"status": "error", "message": "No hay credenciales válidas"})

        fitness_service = build('fitness', 'v1', credentials=creds)
        # Aquí implementaremos la obtención de datos reales
        # Por ahora retornamos datos de ejemplo
        return jsonify({
            "status": "success",
            "data": {
                "pasos": 1000,
                "calorias": 500,
                "distancia": 2.5
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo para desarrollo
    app.run(debug=True)
