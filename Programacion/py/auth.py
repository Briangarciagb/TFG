import os
import firebase_admin
from firebase_admin import db as rtdb
from firebase_admin import credentials  # <-- Agregado si es necesario para manejo dinámico

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import session, url_for, redirect, request

# Definimos los alcances que necesitamos
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

# Ruta absoluta al archivo google_oauth_credentials.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'claves seguras', 'google_oauth_credentials.json')

# Eliminamos la asignación global de "database"
# if firebase_admin._apps:
#     database = rtdb.reference("/")
# else:
#     database = None

def get_credentials():
    """
    Devuelve las credenciales (token) de Google guardadas en la sesión
    """
    creds = None
    if 'credentials' in session:  # Busca credenciales en la sesión
        creds = Credentials(**session['credentials'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                del session['credentials']
                return None
        else:
            return None
        session['credentials'] = creds_to_dict(creds)
    return creds

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

def autorizar():
    """
    Redirige al usuario a la pantalla de consentimiento de Google
    """
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

def oauth2callback():
    """
    Recibe la respuesta de Google, intercambia el 'code' por el token
    y registra/actualiza al usuario en Realtime Database.
    """
    state = session.get('state')
    if not state:
        return "Error: No se encontró el parámetro 'state' en la sesión.", 400

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES, state=state)
    flow.redirect_uri = url_for('callback', _external=True)

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        print("Error al obtener el token:", e)
        return "Error al obtener el token de Google: " + str(e), 400

    # Almacena las credenciales en la sesión
    creds = flow.credentials
    session['credentials'] = creds_to_dict(creds)

    # Obtener info del usuario (ID Token)
    from google.oauth2 import id_token
    from google.auth.transport import requests as g_requests

    try:
        user_info = id_token.verify_oauth2_token(
            creds.id_token,
            g_requests.Request(),
            creds.client_id
        )
    except ValueError as e:
        return f"Error al verificar el ID Token: {str(e)}", 400

    email = user_info.get("email")
    nombre = user_info.get("name", "")
    foto = user_info.get("picture", "")

    # Se obtiene dinámicamente la referencia a la RTDB, considerando que Firebase ya fue inicializado.
    try:
        fb_app = firebase_admin.get_app()
        database_ref = rtdb.reference("/", app=fb_app)
    except ValueError:
        database_ref = None

    # Registramos o actualizamos en Realtime Database
    if database_ref is not None and email:
        email_key = email.replace('.', '_')
        usuario_ref = database_ref.child("usuarios").child(email_key)
        usuario_data = usuario_ref.get()

        if not usuario_data:
            usuario_ref.set({
                "nombre": nombre,
                "email": email,
                "foto": foto,
                "creado_via": "google_oauth"
            })
        else:
            usuario_ref.update({
                "nombre": nombre,
                "foto": foto
            })

    session["user"] = {
        "nombre": nombre,
        "email": email,
        "foto": foto
    }
    # Redireccionar a la página principal en lugar de 'profile'
    return redirect(url_for('principal'))
