import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from auth import autorizar as google_autorizar, oauth2callback, get_credentials
from calendar_api import agregar_evento
from fitness import get_fitness_data, get_sleep_data
from googleapiclient.discovery import build
from datetime import datetime
from flask import send_from_directory



# 1) Calcular la ruta base (la carpeta "Programacion")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 2) Definir las carpetas para plantillas generales y archivos estáticos
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# 3) Definir la carpeta donde se encuentra "loging.html" (carpeta "login")
LOGIN_DIR = os.path.join(BASE_DIR, 'login')

# 4) Definir la carpeta donde estará la plantilla de perfil (carpeta "profile")
PROFILE_DIR = os.path.join(BASE_DIR, 'profile')

# Crear la aplicación Flask usando las rutas definidas
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = "clave_secreta_segura"
CORS(app)

# Agregar carpetas adicionales al buscador de plantillas de Jinja2
app.jinja_loader.searchpath.append(LOGIN_DIR)
app.jinja_loader.searchpath.append(PROFILE_DIR)
# ------------------------Rutas------------------------ #
@app.route('/login/img/<path:filename>')
def serve_login_images(filename):
    return send_from_directory(os.path.join(LOGIN_DIR, 'img'), filename)

# --------------------- Rutas de la aplicación --------------------- #



@app.route('/login')
def login():
    # Renderiza "loging.html" que está en la carpeta "login"
    return render_template('loging.html')

@app.route('/')
def principal():
    # Renderiza la página principal (en la carpeta templates)
    return render_template('Principal.html')

@app.route('/profile')
def profile():
    # Verificar que existan credenciales en la sesión
    if 'credentials' not in session:
        return redirect(url_for('login'))
    
    # Recuperar las credenciales
    creds = get_credentials()
    if not creds:
        return redirect(url_for('login'))
    
    # Usar la API OAuth2 de Google para obtener información del usuario
    oauth2_service = build('oauth2', 'v2', credentials=creds)
    user_info = oauth2_service.userinfo().get().execute()
    
    # Renderiza la plantilla de perfil que está en la carpeta "profile"
    return render_template('profile.html', user=user_info)

@app.route('/pagina')
def pagina():
    return render_template('Pagina.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness.html')

@app.route('/precios')
def precios():
    return render_template('Precios.html')

@app.route('/alimentacion')
def alimentacion():
    return render_template('alimentacion.html')

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/agregar_evento', methods=['POST'])
def evento():
    return agregar_evento()

@app.route('/autorizar')
def autorizar():
    # Inicia el flujo de autorización con Google
    return google_autorizar()

@app.route('/oauth2callback')
def callback():
    # Procesa el callback de OAuth2 y guarda las credenciales
    return oauth2callback()

@app.route('/ver_credenciales')
def ver_credenciales():
    if 'credentials' in session:
        return jsonify(session['credentials'])
    return jsonify({"error": "No se encontraron credenciales."})

# --------------------- Inicio de la aplicación --------------------- #

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)
