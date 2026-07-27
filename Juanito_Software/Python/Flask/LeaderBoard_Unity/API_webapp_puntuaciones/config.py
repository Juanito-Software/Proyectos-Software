import os

from dotenv import load_dotenv

# Carga las variables del archivo .env situado junto a este módulo.
# Sin esto, os.environ no vería nada de lo que hay en el .env.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))


def _requerido(nombre: str) -> str:
    """Lee una variable de entorno obligatoria o aborta con un mensaje claro.

    Preferimos que la aplicación no arranque a que lo haga con una credencial
    por defecto: un valor de respaldo silencioso acaba llegando a producción.
    """
    valor = os.environ.get(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "
            f"Defínela en el archivo .env (ver .env.example)."
        )
    return valor


class Config:
    # Credenciales fuera del código: se leen del entorno.
    SQLALCHEMY_DATABASE_URI = _requerido('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_SUPPORTS_CREDENTIALS = True # Permite que las solicitudes incluyan credenciales (como cookies o encabezados de autenticación).
    # Clave con la que se firman los JWT. Quien la conozca puede fabricar
    # tokens válidos para cualquier usuario, así que nunca va en el código.
    SECRET_KEY = _requerido('SECRET_KEY')
    # Configuración de CORS
    CORS_HEADERS = 'Content-Type','Authorization'# Especifica qué encabezados pueden ser utilizados en las solicitudes CORS.
    CORS_ALLOWED_ORIGINS = [

        # CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad implementado por los navegadores web que permite o restringe las solicitudes HTTP realizadas desde un origen distinto al del servidor que aloja el recurso solicitado.
        # CORS nos serviria en el contexto en el que necesitamos introducir datos externos como origen permitiendo solo acceso a esa url esspecifica
        # Por defecto, la política de mismo origen (Same-Origin Policy) impide que una página web cargue recursos de un dominio diferente al suyo, lo que puede ser una limitación cuando se desarrollan aplicaciones que requieren interactuar con APIs o recursos alojados en otros dominios. 
        # Añade aqui cualquier URL específica que necesites permitir
    ]
