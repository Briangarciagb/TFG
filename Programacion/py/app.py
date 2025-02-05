from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from auth import autorizar as google_autorizar, oauth2callback, get_credentials
from calendar_api import agregar_evento
from fitness import get_fitness_data, get_sleep_data
from googleapiclient.discovery import build
from datetime import datetime
import os

# Configuración de la aplicación Flask
app = Flask(__name__, template_folder='Programacion//templates', static_folder='static')
app.secret_key = "clave_secreta_segura"
CORS(app)

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/pagina')
def pagina():
    return render_template('Pagina.html')

@app.route('/precios')
def precios():
    return render_template('Precios.html')

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

@app.route('/ver_credenciales')
def ver_credenciales():
    if 'credentials' in session:
        return jsonify(session['credentials'])
    return jsonify({"error": "No se encontraron credenciales."})

# Inicio de la aplicación
if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)