# 📌 TFG - Programa de Hospitalización en el Mundo del Desarrollo Web

## 🏥 Descripción del Proyecto
Nuestro Trabajo de Fin de Grado (TFG) consiste en el desarrollo de una **página web centrada en la salud y el bienestar**, con un enfoque especial en la **diabetes, la alimentación saludable y el ejercicio diario**.

### 🎯 Objetivos
1. **Promover una vida saludable** mediante planes de alimentación y entrenamiento personalizados.
2. **Facilitar el seguimiento de la salud** a través de herramientas digitales interactivas.
3. **Desarrollar una infraestructura robusta**, incluyendo un **servidor local** con acceso a través de **OpenVPN**.
4. **Integración con APIs de terceros** como **Google Fit y Samsung Health** para recopilar datos sobre la actividad física.

## 🛠️ Tecnologías Utilizadas
### 💻 Desarrollo Web
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python con Flask
- **Base de Datos**: Firebase Firestore

### 🔌 APIs Integradas
- **Google Fit API**: Para la obtención de datos de actividad física.
- **Samsung Health API**: Para la sincronización con dispositivos Samsung.
- **Google Calendar API**: Para programar eventos y recordatorios de salud.

### 🔒 Seguridad y Autenticación
- **Autenticación con Google OAuth** para el inicio de sesión.
- **Cifrado de contraseñas** con Flask-Bcrypt.

## 🔗 Estructura del Proyecto
```
TFG/
├── Documentos/  # Archivos de documentación
├── Programacion/
│   ├── claves_seguros/
│   │   ├── credentials.json  # Credenciales de Firebase
│   │   ├── SECRET_KEY.env  # Claves de entorno
│   ├── Login/
│   │   ├── login.html  # Interfaz de inicio de sesión
│   │   ├── img/
│   ├── profile/
│   │   ├── profile.html  # Interfaz del perfil del usuario
│   ├── py/
│   │   ├── app.py  # Servidor principal con Flask
│   │   ├── auth.py  # Manejo de autenticación
│   │   ├── fitness.py  # Integración con Google Fit
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── imagenes/
│   ├── templates/
│   │   ├── Principal.html  # Página principal
│   │   ├── alimentacion.html  # Sección de nutrición
│   │   ├── fitness.html  # Planes de entrenamiento
│   │   ├── configuracion.html  # Configuración del usuario
│   │   ├── contacto.html  # Formulario de contacto
│   ├── README.md  # Documentación del proyecto
```

## ⚙️ Implementación del Servidor Local
Nuestro plan es montar un **servidor físico** con acceso a internet y configurarlo para que los usuarios puedan conectarse de forma remota. Este servidor incluirá:
- **Linux como sistema operativo**
- **8GB de RAM**
- **Red conectada directamente al router**
- **Configuración de una VPN (OpenVPN) para acceso seguro**

## 📅 Desarrollo Futuro
En el futuro, planeamos:
- Ampliar la página web con **más funcionalidades interactivas**.
- Implementar una **aplicación móvil** con React Native o Flutter.
- Mejorar la seguridad y escalabilidad del servidor.

## 🏫 Tutores del Proyecto
- **Don Ciro**: Experto en **HTML, JavaScript y CSS**.
- **Elizabeth**: Conocimiento en **diseño de interfaces web**.

---
**Autores**: Brian García Barnicoat y Pablo Ortega Fernández. 🚀

