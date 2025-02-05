import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import session, url_for, redirect, request

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]

# Ruta absoluta al archivo credentials.json
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Ruta base
CREDENTIALS_PATH = os.path.join(BASE_DIR, '../claves seguras/credentials.json')

def get_credentials():
    creds = None
    if 'credentials' in session:  # Busca credenciales almacenadas en la sesión
        creds = Credentials(**session['credentials'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Intenta refrescar el token
            except Exception:
                del session['credentials']  # Elimina credenciales no válidas
                return None
        else:
            return None
        session['credentials'] = creds_to_dict(creds)  # Guarda credenciales en la sesión
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
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

def oauth2callback():
    # Recupera el parámetro 'state' almacenado en la sesión
    state = session.get('state')
    if not state:
        return "Error: No se encontró el parámetro state en la sesión.", 400

    # Crea el flujo, pasando el state recuperado
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES, state=state)
    # Establece el redirect_uri, que debe coincidir exactamente con el registrado en Google Cloud Console
    flow.redirect_uri = url_for('callback', _external=True)
    
    try:
        # Intercambia el código de autorización por un token
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        # Si ocurre un error, se imprime en la consola y se devuelve un mensaje de error
        print("Error al obtener el token:", e)
        return "Error al obtener el token de Google: " + str(e), 400

    # Almacena las credenciales en la sesión para usarlas posteriormente
    session['credentials'] = creds_to_dict(flow.credentials)  # <- AQUÍ ESTABA EL ERROR
    
    # Redirige a la página de perfil, donde se mostrarán los datos del usuario
    return redirect(url_for('profile'))
