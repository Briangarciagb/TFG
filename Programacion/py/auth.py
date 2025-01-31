import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import session, url_for, redirect, request

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/calendar.events'
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
    state = session.get('state')
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES, state=state)
    flow.redirect_uri = url_for('callback', _external=True)
    flow.fetch_token(authorization_response=request.url)
    session['credentials'] = creds_to_dict(flow.credentials)
    return redirect(url_for('principal'))
