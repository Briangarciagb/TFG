from flask import Flask, jsonify
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# Si modificas estos scopes, elimina el archivo token.json
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def get_credentials():
    creds = None
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credenciales.json', SCOPES)
        creds = flow.run_local_server(port=0)
    except Exception as e:
        print(f"Error al obtener credenciales: {e}")
    return creds

@app.route('/conectar')
def conectar():
    try:
        creds = get_credentials()
        return jsonify({"status": "conectado"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/datos')
def obtener_datos():
    try:
        # Aquí puedes agregar la lógica para obtener datos de la API de Google Fitness
        return jsonify({
            "pasos": 0,
            "calorias": 0,
            "distancia": 0
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
