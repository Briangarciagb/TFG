from googleapiclient.discovery import build
from flask import request, jsonify
from datetime import datetime, timedelta
from auth import get_credentials


def create_calendar_event(service, title, start_time, duration=60, description=""):
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (start_time + timedelta(minutes=duration)).isoformat(),
            'timeZone': 'UTC',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')

def agregar_evento():
    creds = get_credentials()
    if not creds:
        return jsonify({"status": "error", "message": "No autorizado"})
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        datos = request.json
        titulo = datos.get('titulo', 'Evento sin título')
        fecha = datetime.strptime(datos.get('fecha'), '%Y-%m-%dT%H:%M:%S')
        duracion = int(datos.get('duracion', 60))
        descripcion = datos.get('descripcion', '')
        enlace = create_calendar_event(service, titulo, fecha, duracion, descripcion)
        
        return jsonify({"status": "success", "evento": enlace})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
