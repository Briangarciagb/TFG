#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, session
import sys
import os
import threading
import time

import firebase_admin
from firebase_admin import credentials, db as rtdb  # Importación de firebase_admin y credentials
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt

# Autenticación con Google (importa funciones de auth.py)
from auth import autorizar as google_autorizar, oauth2callback

# Otros imports (calendar_api, fitness, etc.)
from calendar_api import agregar_evento
from fitness import get_fitness_data, get_sleep_data
from googleapiclient.discovery import build
from datetime import datetime

# Menú en consola
import questionary

# --------------------------------------------------------------------
#                      Configuración de Firebase
# --------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "claves seguras", "firebase_admin_credentials.json")

# Inicializamos la app de Firebase con Realtime Database
if not os.path.exists(CREDENTIALS_PATH):
    print("⚠️ Error: El archivo de credenciales no existe en la ruta:", CREDENTIALS_PATH)
    sys.exit(1)

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://vytalgym-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        database = rtdb.reference("/")
        # Intenta obtener algún dato para confirmar la conexión
        test_value = database.get()
        print("🔥 Realtime Database inicializado correctamente.")
        print("Valor obtenido en la raíz de la BD:", test_value)
    except Exception as e:
        import traceback
        print("⚠️ Error al inicializar Firebase Realtime Database:")
        traceback.print_exc()
        database = None
else:
    database = rtdb.reference("/")

# --------------------------------------------------------------------
#                      Configuración de Flask
# --------------------------------------------------------------------
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
LOGIN_DIR = os.path.join(BASE_DIR, 'Login')
PROFILE_DIR = os.path.join(BASE_DIR, 'profile')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = "clave_secreta_segura"  # Cámbiala por una clave segura real
CORS(app)
bcrypt = Bcrypt(app)

# Agregamos rutas de búsqueda de plantillas
app.jinja_loader.searchpath.append(LOGIN_DIR)
app.jinja_loader.searchpath.append(PROFILE_DIR)

# --------------------------------------------------------------------
#                      Rutas de la Aplicación
# --------------------------------------------------------------------
@app.route('/')
def principal():
    return render_template('Principal.html')

@app.route('/login')
def login():
    # Renderiza la plantilla de login
    return render_template('login.html')

@app.route('/login/img/<path:filename>')
def serve_login_images(filename):
    # Sirve imágenes de la carpeta Login/img
    return send_from_directory(os.path.join(LOGIN_DIR, 'img'), filename)

@app.route('/profile')
def profile():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session["user"])

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))

# Definición de rutas en Flask
@app.route('/ruta_post', methods=['POST'])
def ruta_post():
    # Código para manejar la solicitud POST
    return "Solicitud POST recibida"

@app.route('/ruta_get', methods=['GET'])
def ruta_get():
    # Código para manejar la solicitud GET
    return "Solicitud GET recibida"

# --------------------------------------------------------------------
#                      Rutas para Registro/Login (local)
# --------------------------------------------------------------------
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    if database is None:
        return "No se pudo conectar a Realtime Database", 500

    data = request.form
    email = data.get('email')
    nombre = data.get('nombre')
    password = data.get('password')

    if not email or not nombre or not password:
        return "❌ Todos los campos son obligatorios.", 400

    # Reemplazamos '.' por '_' para la key en Realtime Database
    email_key = email.replace('.', '_')
    usuario_ref = database.child("usuarios").child(email_key)
    usuario_data = usuario_ref.get()

    if usuario_data:
        return "❌ El usuario ya está registrado.", 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    usuario_ref.set({
        "nombre": nombre,
        "email": email,
        "password": hashed_password
    })

    return redirect(url_for('login'))

@app.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    if database is None:
        return "No se pudo conectar a Realtime Database", 500

    data = request.form
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return "❌ Debes ingresar email y contraseña.", 400

    email_key = email.replace('.', '_')
    usuario_ref = database.child("usuarios").child(email_key)
    usuario_data = usuario_ref.get()

    if not usuario_data:
        return "❌ Usuario no encontrado.", 404

    # Verificamos la contraseña con Bcrypt
    if bcrypt.check_password_hash(usuario_data["password"], password):
        session["user"] = {
            "nombre": usuario_data["nombre"],
            "email": usuario_data["email"]
        }
        return redirect(url_for('profile'))
    else:
        return "❌ Contraseña incorrecta.", 401

# --------------------------------------------------------------------
#          Rutas de otras páginas (ejemplos)
# --------------------------------------------------------------------
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

@app.route('/salud', methods=['GET'])
def salud():
    user = None
    if 'user' in session:
        user = session['user']
    return render_template('salud.html', user=user)




# --------------------------------------------------------------------
#             Integración con APIs y Google OAuth
# --------------------------------------------------------------------
@app.route('/agregar_evento', methods=['POST'])
def evento():
    return agregar_evento()

@app.route('/autorizar')
def autorizar():
    return google_autorizar()

@app.route('/oauth2callback')
def callback():
    return oauth2callback()

# --------------------------------------------------------------------
#           Variables y funciones para el servidor en 2º plano
# --------------------------------------------------------------------
server_thread = None

def iniciar_servidor_en_segundo_plano():
    """
    Inicia Flask en un thread (daemon) para no bloquear la CLI principal.
    """
    global server_thread
    if server_thread and server_thread.is_alive():
        print("⚠️ El servidor Flask ya está corriendo.\n")
        return

    print("\n🚀🔥 ¡El servidor Flask se está iniciando en segundo plano! 🔥🚀")
    server_thread = threading.Thread(
        target=lambda: app.run(debug=True, use_reloader=False),
        daemon=True
    )
    server_thread.start()

    time.sleep(2)
    print("   Accede a http://127.0.0.1:5000/ para ver la aplicación.\n")

def submenu_servidor():
    """
    Submenú que aparece después de iniciar el servidor.
    """
    while True:
        choice = questionary.select(
            "El servidor Flask está corriendo en segundo plano. ¿Qué deseas hacer ahora?",
            choices=[
                "🔙 Volver al menú principal",
                "❌ Salir (detener servidor)"
            ]
        ).ask()

        if choice == "🔙 Volver al menú principal":
            return
        elif choice == "❌ Salir (detener servidor)":
            print("Saliendo... El servidor se cerrará al terminar el proceso.")
            sys.exit(0)

# --------------------------------------------------------------------
#                      Funciones de Menú principal
# --------------------------------------------------------------------
def mostrar_banner():
    banner = r"""
 <!-- ************************************************************************* -->
<!-- * __  __           __             ___    ____                           * -->
<!-- */\ \/\ \         /\ \__         /\_ \  /\  _`\                         * -->
<!-- *\ \ \ \ \  __  __\ \ ,_\    __  \//\ \ \ \ \L\_\  __  __    ___ ___    * -->
<!-- * \ \ \ \ \/\ \/\ \\ \ \/  /'__`\  \ \ \ \ \ \L_L /\ \/\ \ /' __` __`\  * -->
<!-- *  \ \ \_/ \ \ \_\ \\ \ \_/\ \L\.\_ \_\ \_\ \ \/, \ \ \_\ \/\ \/\ \/\ \ * -->
<!-- *   \ `\___/\/`____ \\ \__\ \__/.\_\/\____\\ \____/\/`____ \ \_\ \_\ \_\* -->
<!-- *    `\/__/  `/___/> \\/__/\/__/\/_/\/____/ \/___/  `/___/> \/_/\/_/\/_/* -->
<!-- *               /\___/                                 /\___/           * -->
<!-- *               \/__/                                  \/__/            * -->
<!-- ************************************************************************* -->
    """
    print(banner)
    print("Bienvenido al asistente de configuración de VytalGym\n")
    print("Hecho por Brian y Pablo\n")

def iniciar_firebase():
    print("\n🔥 Ejecutando 'firebase init'...\n")
    os.system("firebase init")
    print("\n✅ Firebase se ha inicializado.\n")

def vincular_google():
    print("\n🌐 Vinculando la página con Google OAuth...\n")
    print("🔗 Llamando a la ruta /autorizar (ejemplo)...")
    print("✅ Vinculación con Google completada (ejemplo).\n")

def menu_principal():
    """
    Menú principal con Questionary (checkbox).
    Selecciona múltiples tareas y las ejecuta secuencialmente.
    """
    opciones = [
        questionary.Choice(title="🚀 Iniciar servidor", value="iniciar_servidor"),
        questionary.Choice(title="🔥 Iniciar Firebase", value="firebase_init"),
        questionary.Choice(title="🌐 Vincular la página con Google (OAuth)", value="vincular_google"),
        questionary.Choice(title="❌ Salir", value="salir"),
    ]

    seleccionadas = questionary.checkbox(
        "¿Qué deseas hacer?\n(Flechas ↑↓ para moverte, Espacio para seleccionar, Enter para continuar):",
        choices=opciones
    ).ask()

    return seleccionadas or []

def ejecutar_configuracion(opciones_seleccionadas):
    """
    Procesa las opciones seleccionadas en orden.
    """
    if not opciones_seleccionadas:
        print("No se ha seleccionado ninguna opción. Finalizando...\n")
        return

    print("Procesando las opciones seleccionadas...\n")

    for opcion in opciones_seleccionadas:
        if opcion == "iniciar_servidor":
            iniciar_servidor_en_segundo_plano()
            submenu_servidor()

        elif opcion == "firebase_init":
            iniciar_firebase()

        elif opcion == "vincular_google":
            vincular_google()

        elif opcion == "salir":
            print("Saliendo del asistente...")
            sys.exit(0)

    print("¡Operaciones completadas!\n")

def iniciar_asistente():
    """
    Bucle principal: muestra banner, menú, ejecuta opciones, repite.
    """
    while True:
        mostrar_banner()
        opciones = menu_principal()
        if not opciones:
            print("No has seleccionado nada. Finalizando...\n")
            break
        ejecutar_configuracion(opciones)

# --------------------------------------------------------------------
#                           Punto de entrada
# --------------------------------------------------------------------
if __name__ == "__main__":
    iniciar_asistente()