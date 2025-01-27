from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"  # Cambia esto en producción
CORS(app)

SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.body.read'
]

def get_credentials():
    creds = None
    if 'credentials' in session:
        creds = Credentials(**session['credentials'])
    # Verifica si las credenciales existen o son válidas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                # Si falla el refresh, eliminamos de sesión
                del session['credentials']
                return None
        else:
            return None
        
        # Actualiza en la sesión
        session['credentials'] = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
    return creds

def get_fitness_data(service, date):
    """
    Obtener datos básicos: pasos, calorías y distancia.
    Puedes añadir más data sources si deseas.
    """
    start = datetime(date.year, date.month, date.day).timestamp() * 1000000000
    end = (datetime(date.year, date.month, date.day) + timedelta(days=1)).timestamp() * 1000000000
    
    steps_data_source = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    calories_data_source = "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
    
    dataset = f"{int(start)}-{int(end)}"
    
    try:
        steps_data = service.users().dataSources().datasets().get(
            userId="me",
            dataSourceId=steps_data_source,
            datasetId=dataset
        ).execute()
        
        calories_data = service.users().dataSources().datasets().get(
            userId="me",
            dataSourceId=calories_data_source,
            datasetId=dataset
        ).execute()
        
        # Procesar pasos
        steps_points = steps_data.get('point', [])
        total_steps = sum(int(point['value'][0]['intVal']) for point in steps_points)
        
        # Procesar calorías
        calories_points = calories_data.get('point', [])
        total_calories = sum(
            float(point['value'][0]['fpVal']) 
            for point in calories_points if 'fpVal' in point['value'][0]
        )
        
        # Aproximación de distancia a partir de pasos
        distance = total_steps * 0.0007  # en km (aprox.)
        
        return {
            "pasos": total_steps,
            "calorias": round(total_calories, 2),
            "distancia": round(distance, 2)
        }
    except Exception as e:
        print(f"Error obteniendo datos de actividad: {e}")
        return {"pasos": 0, "calorias": 0, "distancia": 0}

def get_sleep_data(service, date):
    """
    Obtener datos de sueño para la fecha dada.
    """
    start = datetime(date.year, date.month, date.day).timestamp() * 1000000000
    end = (datetime(date.year, date.month, date.day) + timedelta(days=1)).timestamp() * 1000000000

    sleep_data_source = "derived:com.google.sleep.segment:com.google.android.gms:merge_sleep_segments"
    
    dataset = f"{int(start)}-{int(end)}"
    
    try:
        sleep_data = service.users().dataSources().datasets().get(
            userId="me",
            dataSourceId=sleep_data_source,
            datasetId=dataset
        ).execute()
        
        sleep_points = sleep_data.get('point', [])
        
        # Filtramos los segmentos de sueño (excluyendo los despierto o fuera de la cama)
        total_sleep_minutes = sum(
            (int(point['endTimeNanos']) - int(point['startTimeNanos'])) / (1000 * 60 * 1000000)
            for point in sleep_points
            if point['value'][0]['intVal'] not in [1, 3]  
        )
        
        return {"sueno": round(total_sleep_minutes / 60, 2)}  # En horas
    except Exception as e:
        print(f"Error obteniendo datos de sueño: {e}")
        return {"sueno": 0}

# ------------------ RUTAS FLASK ------------------
@app.route('/')
def principal():
    return render_template('Principal.html')

@app.route('/fitness')
def fitness():
    """
    Aquí se muestra la página de Fitness.
    El JavaScript interno llamará a /datos para traer la info.
    """
    return render_template('fitness.html')

@app.route('/alimentacion')
def alimentacion():
    return render_template('alimentacion.html')

@app.route('/configuracion')
def configuracion():
    """
    Nueva página con el botón para conectar a Google Fit
    """
    return render_template('configuracion.html')


@app.route('/autorizar')
def autorizar():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',  # Ajusta si tu JSON se llama distinto
        SCOPES
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state', None)
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return redirect(url_for('principal'))

@app.route('/datos', methods=['POST'])
def obtener_datos():
    """
    Endpoint para obtener datos de actividad y sueño de Google Fit.
    Espera un JSON con { "fecha": "YYYY-MM-DD" }
    """
    creds = get_credentials()
    if not creds:
        return jsonify({
            "status": "error",
            "message": "No autorizado"
        })
    
    try:
        fecha_seleccionada_str = request.json.get('fecha')
        fecha_seleccionada = datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d')
        
        service = build('fitness', 'v1', credentials=creds)
        
        fitness_data = get_fitness_data(service, fecha_seleccionada)
        sleep_data = get_sleep_data(service, fecha_seleccionada)
        
        # Retorna un JSON con todos los datos disponibles
        return jsonify({
            "status": "success",
            "data": {**fitness_data, **sleep_data}
        })
        
    except Exception as e:
        print(f"Error al obtener datos: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    # Solo para desarrollo (deshabilita verificación HTTPS)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)
