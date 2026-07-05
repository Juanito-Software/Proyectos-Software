import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://client:sesamoPass1?@localhost:5432/game'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_SUPPORTS_CREDENTIALS = True # Permite que las solicitudes incluyan credenciales (como cookies o encabezados de autenticación).
    SECRET_KEY = '6Nj3G€%l&k!YgFs8P?fds'# Clave secreta utilizada por Flask para sesiones y otras operaciones de seguridad.
    # Configuración de CORS
    CORS_HEADERS = 'Content-Type','Authorization'# Especifica qué encabezados pueden ser utilizados en las solicitudes CORS.
    CORS_ALLOWED_ORIGINS = [

        # CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad implementado por los navegadores web que permite o restringe las solicitudes HTTP realizadas desde un origen distinto al del servidor que aloja el recurso solicitado.
        # CORS nos serviria en el contexto en el que necesitamos introducir datos externos como origen permitiendo solo acceso a esa url esspecifica
        # Por defecto, la política de mismo origen (Same-Origin Policy) impide que una página web cargue recursos de un dominio diferente al suyo, lo que puede ser una limitación cuando se desarrollan aplicaciones que requieren interactuar con APIs o recursos alojados en otros dominios. 
        # Añade aqui cualquier URL específica que necesites permitir
    ]
