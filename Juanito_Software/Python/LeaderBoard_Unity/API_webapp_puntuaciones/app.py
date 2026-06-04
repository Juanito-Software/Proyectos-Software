from flask import Flask, request, jsonify, render_template_string  
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from flask_mail import Mail, Message
from functools import wraps
from models import db, Puntuacion, Jugadores, Privacidad, NivelPrivacidad, Amistad, PuntuacionHistorico, LogroJugador, Logros
from config import Config
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import re
import hashlib
import os

# Clave secreta para generar el token JWT (debe ser segura y mantenerse oculta)


app = Flask(__name__)
app.config.from_object(Config)

# Configurar CORS usando la configuración de la clase Config
CORS(app, methods=["GET", "POST", "DELETE", "PUT"], origins=Config.CORS_ALLOWED_ORIGINS)

#db=SQLAlchemy(app)
db.init_app(app)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # O el servidor SMTP de tu elección
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False           # No usar SSL (ya que TLS está activado)
app.config['MAIL_USERNAME'] = 'deadvalleygame@gmail.com'  # Tu email
app.config['MAIL_PASSWORD'] = 'jgvn mdyn vhrz mtvv'  # Tu contraseña de correo
app.config['MAIL_DEFAULT_SENDER'] = 'deadvalleygame@gmail.com'  # Dirección desde la que se enviarán los correos

mail = Mail(app)  # Inicializa Flask-Mail



def authenticate_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        

        if auth_header:
            token = auth_header.split(" ")[1]  # Se espera el formato "Bearer <token>"
            # print(f"Token recibido: {token}")
        if not token:
            print(f"Response: Token no proporcionado: {403}")
            return jsonify({'error': 'Token no proporcionado'}), 403

        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['id']
        except jwt.ExpiredSignatureError:
            # Realiza el print antes de retornar
            print(f"Response: El token ha expirado, Status Code: {401}")
            return jsonify({'error': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            print(f"Response: Token inválido, Status Code: {403}")
            return jsonify({'error': 'Token inválido'}), 403

        return f(*args, **kwargs)

    return decorator



# Decorador de fábrica para aceptar parámetros
# Necesario el rol admin
def authenticate_token2(required_role="admin"):
    def decorator(f):
        @wraps(f)  # Esto mantiene la firma de la función original
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')

            if not token:
                print(f"Response: Token no proporcionado: {403}")
                return jsonify({'error': 'Token no proporcionado'}), 403

            try:
                payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload['id']
                
                # Si se requiere verificar el rol
                if required_role:
                    jugador = Jugadores.query.get(request.user_id)
                    if not jugador:
                        print(f"Response: Acceso denegado: Jugador no encontrado: {404}")
                        return jsonify({'error': f'Acceso denegado: Jugador no encontrado'}), 404
                    if jugador.rol != required_role:
                        print(f"Response: Acceso denegado: se requiere rol de {required_role}: {403}")
                        return jsonify({'error': f'Acceso denegado: se requiere rol de {required_role}'}), 403
            except jwt.ExpiredSignatureError:
                print(f"Response: El token ha expirado, Status Code: {401}")
                return jsonify({'error': 'El token ha expirado'}), 401
            except jwt.InvalidTokenError:
                print(f"Response: Token inválido, Status Code: {403}")
                return jsonify({'error': 'Token inválido'}), 403

            return f(*args, **kwargs)
        
        return wrapper
    
    return decorator

"""
@app.route('/jugadores/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.headers.get('Authorization')

    if not refresh_token:
        return jsonify({'error': 'Refresh Token no proporcionado'}), 403

    try:
        # Decodificar el Refresh Token
        payload = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=['HS256'])
        jugador_id = payload['id']

        # Verificar que el Refresh Token coincida con el almacenado en la base de datos
        jugador = Jugadores.query.get(jugador_id)
        if not jugador or jugador.refresh_token != refresh_token:
            return jsonify({'error': 'Refresh Token inválido'}), 403

        # Generar un nuevo Access Token
        new_access_token = jwt.encode(
            {
                'id': jugador.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )

        return jsonify({'access_token': new_access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'El Refresh Token ha expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Refresh Token inválido'}), 403
"""



@app.route('/jugadores/<int:id>', methods=['DELETE'])
@authenticate_token
def eliminar_usuario(id):
    try:
        # Buscar al jugador por ID
        jugador = Jugadores.query.get(id)
        if not jugador:
            return jsonify({'error': 'Jugador no encontrado'}), 404

        # Eliminar los registros relacionados en la tabla 'privacidad'
        privacidad_registros = Privacidad.query.filter_by(jugador_id=id).all()
        for privacidad in privacidad_registros:
            db.session.delete(privacidad)

        # Eliminar las relaciones de amistad del jugador
        amistades = Amistad.query.filter((Amistad.jugador_solicitante_id == id) | (Amistad.jugador_receptor_id == id)).all()
        for amistad in amistades:
            db.session.delete(amistad)

        # Eliminar las puntuaciones asociadas al jugador
        puntuaciones = Puntuacion.query.filter_by(jugador_id=id).all()
        for puntuacion in puntuaciones:
            db.session.delete(puntuacion)

        # Eliminar el jugador
        db.session.delete(jugador)
        db.session.commit()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200

    except Exception as e:
        db.session.rollback()  # Deshacer cambios en caso de error
        print(f"Error al eliminar usuario: {str(e)}")  # Log para identificar el error exacto
        return jsonify({'error': f'Error al eliminar el usuario: {str(e)}'}), 500



@app.route('/jugadores/register', methods=['POST'])
def register_player():
    data = request.get_json()
    print(data)  # Añadir para ver qué datos llegan al servidor

    nombre = data.get('nombre')
    # Asumiendo que tienes contraseñas en tu modelo
    password_hash = generate_password_hash(data.get('password'))
    email = data.get('email')
    numtelefono = data.get('numtelefono')
    rol = data.get('rol', 'jugador')  # Si no se proporciona rol, asigna 'jugador' por defecto

    # Validaciones básicas
    if not nombre or not email or not numtelefono or not password_hash:
        print(f"Response: Todos los campos son obligatorios: {400}")
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    if len(nombre) > 12 or len(numtelefono) != 9:
        print(f"Response: El nombre debe tener hasta 12 caracteres y el número de teléfono 9 dígitos: {400}")
        return jsonify({'error': 'El nombre debe tener hasta 12 caracteres y el número de teléfono 9 dígitos'}), 400

    if Jugadores.query.filter_by(email=email).first():
        print(f"Response: El correo electrónico ya está registrado: {400}")
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 400

    try:
        # Crear el jugador
        nuevo_jugador = Jugadores(nombre=nombre, password=password_hash,  email=email, numtelefono=numtelefono, rol=rol)
        
        # Guardar ambos en la base de datos
        db.session.add(nuevo_jugador)
        db.session.commit()

        # Crear relación de amistad consigo mismo
        relacion_amistad = Amistad(
            jugador_solicitante_id=nuevo_jugador.id,
            jugador_receptor_id=nuevo_jugador.id,
            estado="aceptado"  # Estado inicial de la relación
        )
        db.session.add(relacion_amistad)
        db.session.commit()


        return jsonify({
            'message': 'Jugador registrado exitosamente',
            'jugador': {'id': nuevo_jugador.id, 'nombre': nuevo_jugador.nombre},
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar el jugador: {str(e)}: {500}")  # Esto imprimirá el error en el servidor
        return jsonify({'error': f'Error al registrar el jugador: {str(e)}'}), 500




@app.route('/jugadores/send-reset-email', methods=['POST'])
def send_reset_email():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        print(f"Response: El correo es obligatorio: {400}")
        return jsonify({'error': 'El correo es obligatorio; Error 400'}), 400

    # Verificar si el correo está registrado en la base de datos
    usuario = Jugadores.query.filter_by(email=email).first()
    if not usuario:
        print(f"Response: El correo no está registrado: {400}")
        return jsonify({'error': 'El correo no está registrado; Error 400_2'}), 400

     # Crear un token JWT para restablecer la contraseña
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=0.2)

    # Creamos el payload con el correo del usuario y la fecha de expiración
    payload = {
        'email': email,
        'exp': expiration_time
    }

    # Generar el token JWT
    reset_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    # Crear la URL del restablecimiento de contraseña con el token JWT
    reset_url = f'http://localhost:5000/jugadores/reset-password/{reset_token}'

    # Crear el mensaje de correo
    subject = 'Restablece tu contraseña'
    message = f'Haz clic en el siguiente enlace para restablecer tu contraseña:\n{reset_url}'

    msg = Message(subject=subject,
                  recipients=[email],  # Correo del destinatario
                  body=message)

    try:
        # Envía el correo
        mail.send(msg)
        print(f"Response: Correo enviado exitosamente: {200}")
        return jsonify({'message': 'Correo enviado exitosamente'}), 200
    except Exception as e:
        print("Error al enviar el correo:", e)
        return jsonify({'error': f'Error al enviar el correo: {str(e)}'}), 500


@app.route('/jugadores/reset-password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):

    try:
        # Decodificar el token JWT
        payload = jwt.decode(reset_token, app.config['SECRET_KEY'], algorithms=['HS256'])

        email = payload.get('email')

        # Buscar el usuario que tiene este correo
        usuario = Jugadores.query.filter_by(email=email).first()

        # Verificar si el usuario existe
        if not usuario:
            print(f"Response: El usuario no existe: {400}")
            return jsonify({'error': 'El usuario no existe; Error 400_3'}), 400

        # Verificar si el token ha expirado
        if payload.get('exp') < datetime.now(timezone.utc).timestamp():
            print(f"Response: El token ha expirado: {401}")
            return jsonify({'error': 'El token ha expirado; Error 401 '}), 401 

        if request.method == 'POST':
            # Obtener la nueva contraseña desde el formulario
            new_password = request.form.get('password')
            repeat_password = request.form.get('repeatpassword')

            # Validar que ambos campos estén presentes
            if not new_password or not repeat_password:
                print(f"Response: Ambos campos de contraseña son obligatorios: {400}")
                return jsonify({'error': 'Ambos campos de contraseña son obligatorios; Error 400_5'}), 400

            # Comprobar si las contraseñas coinciden
            if new_password != repeat_password:
                print(f"Response: Las contraseñas no coinciden: {400}")
                return jsonify({'error': 'Las contraseñas no coinciden; Error 400_6'}), 400

            # Guardar la nueva contraseña en la base de datos
            usuario.password = generate_password_hash(new_password)
            db.session.commit()

            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Contraseña Restablecida</title>
            </head>
            <body>
                <h1>Contraseña restablecida exitosamente</h1>
                <p>Ahora puedes iniciar sesión con tu nueva contraseña.</p>
            </body>
            </html>
            """)

        # Si la solicitud es GET, informar al usuario que debe enviar la nueva contraseña
        reset_password_form = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Restablecer Contraseña</title>
        </head>
        <body>
            <h1>Restablecer Contraseña</h1>
            <form method="POST" action="">
                <label for="password">Nueva Contraseña:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                <label for="repeatpassword">Repite la Contraseña:</label><br>
                <input type="password" id="repeatpassword" name="repeatpassword" required><br><br>
                <button type="submit">Restablecer</button>
            </form>
        </body>
        </html>
        """
        return render_template_string(reset_password_form)

    except jwt.ExpiredSignatureError:
        print(f"Response: El token ha expirado: {400}")
        return jsonify({'error': 'El token ha expirado; Error 400_7'}), 400
    except jwt.InvalidTokenError:
        print(f"Response: Token inválido: {401}")
        return jsonify({'error': 'Token inválido; Error 401'}), 401
        


@app.route('/jugadores/login', methods=['POST'])
def login():
    data = request.get_json()

    nombre = data.get('nombre')
    password = data.get('password')  # Asumiendo que tienes contraseñas en tu modelo

    # Validaciones básicas
    if not nombre or not password:
        print(f"Response: nombre y contraseña son obligatorios: {400}")
        return jsonify({'error': 'nombre y contraseña son obligatorios; Error 400'}), 400

    try:
        # Buscar el jugador por nombre
        jugador = Jugadores.query.filter_by(nombre=nombre).first()
        if not jugador:
            print(f"Response: Jugador no encontrado: {404}")
            return jsonify({'error': 'Jugador no encontrado'}), 404
        # Verificar si la contraseña es válida
        if not check_password_hash(jugador.password, password):
            print(f"Response: Contraseña incorrectos: {401}")
            return jsonify({'error': 'Contraseña incorrectos; Error 401'}), 401

        # Generar token JWT
        access_token = jwt.encode(
            {
                'id': jugador.id,
                'exp': datetime.now(timezone.utc) + timedelta(hours=2)  # El token expira en 2 horas
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )

        # Generar Refresh Token
        refresh_token = jwt.encode(
            {
                'id': jugador.id,
                'exp': datetime.now(timezone.utc) + timedelta(days=7)
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )

        # Guardar el Refresh Token en la base de datos
        jugador.refresh_token = refresh_token  # Añade un campo `refresh_token` en tu modelo de Jugadores
        db.session.commit()

        return jsonify({
            'message': 'Login exitoso',
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        print(f"Error al iniciar sesión: {str(e)}")  # Esto imprimirá el error en el servidor
        return jsonify({'error': f'Error al iniciar sesión: {str(e)}'}), 500

@app.route('/jugadores/refresh_token', methods=['POST'])
def refresh_token():
    data = request.get_json()

    # Obtener el refresh token enviado por el cliente
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        print("Response: Refresh token es obligatorio: 400")
        return jsonify({'error': 'Refresh token es obligatorio'}), 400

    try:
        # Verificar si el refresh token es válido
        decoded_token = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=['HS256'])

        # Buscar el jugador por ID del refresh token
        jugador = Jugadores.query.filter_by(id=decoded_token['id']).first()
        if not jugador:
            print("Response: Jugador no encontrado: 404")
            return jsonify({'error': 'Jugador no encontrado'}), 404

        # Generar un nuevo access token
        access_token = jwt.encode(
            {
                'id': jugador.id,
                'exp': datetime.now(timezone.utc) + timedelta(hours=2)  # El nuevo access token expira en 2 horas
            },
            Config.SECRET_KEY,
            algorithm='HS256'
        )

        return jsonify({
            'message': 'Refresh token exitoso',
            'access_token': access_token
        }), 200

    except jwt.ExpiredSignatureError:
        print("Response: Refresh token ha expirado: 401")
        return jsonify({'error': 'Refresh token ha expirado'}), 401
    except jwt.InvalidTokenError:
        print("Response: Refresh token no válido: 401")
        return jsonify({'error': 'Refresh token no válido'}), 401
    except Exception as e:
        print(f"Error al refrescar el token: {str(e)}")
        return jsonify({'error': f'Error al refrescar el token: {str(e)}'}), 500








@app.route('/jugadores/perfil', methods=['GET'])
@authenticate_token  # Protege esta ruta
def perfil():
    user_id = request.user_id  # Esto fue extraído del payload del JWT en el decorador
    jugador = Jugadores.query.get(user_id)
    if jugador:
        return jsonify({
            'id': jugador.id,
            'nombre': jugador.nombre,
            'email': jugador.email,
            'numtelefono': jugador.numtelefono
        })
    else:
        print(f"Response: Jugador no encontrado: {404}")
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/jugadores/perfil', methods=['PUT'])
@authenticate_token
def actualizar_perfil():
    data = request.json
    if not data or 'nombre' not in data or 'email' not in data or 'numtelefono' not in data:
        print(f"Response: Datos incompletos: {400}")
        return jsonify({'error': 'Datos incompletos'}), 400

    # Validar formato del correo electrónico
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, data['email']):
        print(f"Response: Email inválido: {400}")
        return jsonify({'error': 'Formato de correo electrónico inválido'}), 400
    
    jugador = Jugadores.query.get(request.user_id)
    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404
    
    nombre = data.get('nombre', jugador.nombre)
    email = data.get('email', jugador.email)
    numtelefono = data.get('numtelefono', jugador.numtelefono)
    
    try:
        # Actualizar campos específicos
        jugador.nombre = nombre
        jugador.email = email
        jugador.numtelefono = numtelefono

        db.session.commit()
        return jsonify({'mensaje': 'Perfil actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar el perfil: {e}")  # Log del error en la consola
        return jsonify({'error': f'Error al actualizar perfil: {str(e)}'}), 500






""""
@app.route('/puntuaciones', methods=['POST'])
@authenticate_token
def agregar_puntuacion():
    data = request.json  # Si los datos vienen en formato JSON
    nombre = data.get('nombre')  # Nombre del jugador (requerido)
    valor = data.get('valor')   # Valor de la puntuación (requerido)

    # Validar que los campos requeridos estén presentes
    if not nombre or not valor:
        return jsonify({'error': 'El nombre del jugador y el valor de la puntuación son obligatorios'}), 400

    try:
        valor = int(valor)
    except ValueError:
        return jsonify({'error': 'El valor de la puntuación debe ser un número entero'}), 400

    # Verificar si el jugador existe en la tabla 'jugadores'
    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': f"No se encontró un jugador con el nombre '{nombre}'"}), 404

    # Verificar si ya existe una puntuación para este jugador
    puntuacion_existente = Puntuacion.query.filter_by(jugador_id=jugador.id).first()
    if puntuacion_existente:
        return jsonify({'error': 'Ya existe una puntuación con este valor para el jugador'}), 409

    # Crear una nueva puntuación asociada al jugador
    nueva_puntuacion = Puntuacion(valor=valor, jugador_id=jugador.id)
    db.session.add(nueva_puntuacion)
    db.session.commit()

    # Devolver la respuesta con los datos de la puntuación agregada
    return jsonify({
        'id': nueva_puntuacion.id,
        'valor': nueva_puntuacion.valor,
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
    }), 201


@app.route('/puntuaciones/<string:nombre>', methods=['PUT'])
@authenticate_token
def actualizar_puntuacion(nombre):
    print(f"Actualizando puntuacion")
    data = request.json  # Datos enviados en formato JSON
    nuevo_valor = data.get('valor')

    # Verificar que el valor esté presente
    if nuevo_valor is None:
        return jsonify({'error': 'Debe proporcionar un valor para actualizar'}), 400

    try:
        # Buscar al jugador por nombre
        jugador = Jugadores.query.filter_by(nombre=nombre).first()
        if not jugador:
            return jsonify({'error': f"No se encontró un jugador con el nombre '{nombre}'"}), 404

        # Buscar la puntuación del jugador
        puntuacion = Puntuacion.query.filter_by(jugador_id=jugador.id).first()
        if not puntuacion:
            return jsonify({'error': 'Puntuación no encontrada para el jugador especificado'}), 404

        # Verificar si el nuevo valor es mayor que la puntuación actual
        if int(nuevo_valor) <= puntuacion.valor:
            return jsonify({'error': 'La nueva puntuación debe ser mayor que la actual'}), 422

        # Actualizar el valor proporcionado
        puntuacion.valor = int(nuevo_valor)

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Devolver la puntuación actualizada
        return jsonify({
            'id': puntuacion.id,
            'valor': puntuacion.valor,
            'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
        }), 200

    except ValueError:
        db.session.rollback()
        return jsonify({'error': 'El valor debe ser un entero'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
"""

@app.route('/puntuaciones', methods=['POST'])
@authenticate_token
def agregar_o_actualizar_puntuacion():
    data = request.json  # Si los datos vienen en formato JSON
    nombre = data.get('nombre')  # Nombre del jugador (requerido)
    valor = data.get('valor')   # Valor de la puntuación (requerido)

    # Validar que los campos requeridos estén presentes
    if not nombre or not valor:
        return jsonify({'error': 'El nombre del jugador y el valor de la puntuación son obligatorios'}), 400

    try:
        valor = int(valor)
    except ValueError:
        return jsonify({'error': 'El valor de la puntuación debe ser un número entero'}), 400

    # Verificar si el jugador existe en la tabla 'jugadores'
    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': f"No se encontró un jugador con el nombre '{nombre}'"}), 404

    # Verificar si ya existe una puntuación para este jugador
    puntuacion_existente = Puntuacion.query.filter_by(jugador_id=jugador.id).first()
    if puntuacion_existente:
        # Si la puntuación existe, se actualiza
        if valor > puntuacion_existente.valor:  # Solo se actualiza si el nuevo valor es mayor
            puntuacion_existente.valor = valor
            db.session.commit()
            return jsonify({
                'id': puntuacion_existente.id,
                'valor': puntuacion_existente.valor,
                'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
            }), 200
        else:
            return jsonify({'error': 'La nueva puntuación debe ser mayor que la actual'}), 422
    else:
        # Si no existe, se crea una nueva puntuación
        nueva_puntuacion = Puntuacion(valor=valor, jugador_id=jugador.id)
        db.session.add(nueva_puntuacion)
        db.session.commit()
        return jsonify({
            'id': nueva_puntuacion.id,
            'valor': nueva_puntuacion.valor,
            'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
        }), 201



@app.route('/puntuaciones', methods=['GET'])
@authenticate_token
def obtener_puntuaciones():

    # Parámetros
    order_by = request.args.get('order_by', 'valor')  # Por defecto, ordenamos por 'valor'
    order = request.args.get('order', 'desc')  # Por defecto, en orden descendente
    page = request.args.get('page', 1)  # Página 1 por defecto
    per_page = request.args.get('per_page', 15)  # 15 elementos por página por defecto

    # Validación de los parámetros
    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        return jsonify({'error': 'Los parámetros de paginación deben ser enteros'}), 400 

    # Validar el campo de ordenamiento
    if not hasattr(Puntuacion, order_by):
        return jsonify({'error': f"El campo '{order_by}' no es válido para ordenar"}), 422 

    # Validar el tipo de orden (asc o desc)
    if order not in ['asc', 'desc']:
        return jsonify({'error': "El valor de 'order' debe ser 'asc' o 'desc'"}), 422 

     # Subconsulta para verificar si existe una relación de amistad
    amistad_subquery = db.session.query(Amistad.id).filter(
        ((Amistad.jugador_solicitante_id == Puntuacion.jugador_id) &
         (Amistad.jugador_receptor_id == request.user_id)) |
        ((Amistad.jugador_receptor_id == Puntuacion.jugador_id) &
         (Amistad.jugador_solicitante_id == request.user_id)),
        Amistad.estado == 'aceptado'
    ).exists()

    # Ordenar las puntuaciones según los parámetros y asegurarse de que los jugadores sean públicos
    try:
        puntuaciones = Puntuacion.query.join(Jugadores) \
            .join(Privacidad) \
            .filter(
                (Privacidad.nivel_de_privacidad == 'publico') |  # Público
                ((Privacidad.nivel_de_privacidad == 'amigos') &  amistad_subquery)# Amigos
                 
            ) \
            .order_by(
                getattr(Puntuacion, order_by).desc() if order == 'desc' else getattr(Puntuacion, order_by).asc()
            ) \
            .paginate(page=page, per_page=per_page)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Si no hay resultados
    if not puntuaciones.items:
        return jsonify({'mensaje': 'No se encontraron puntuaciones'}), 404

    # Formatear los resultados en JSON, obteniendo el nombre del jugador desde la relación
    resultado = [{'id': p.id, 'nombre': p.jugador.nombre, 'valor': p.valor} for p in puntuaciones.items]

    # Devolver los datos con información de paginación
    return jsonify({
        'puntuaciones': resultado,
        'page': puntuaciones.page,
        'per_page': puntuaciones.per_page,
        'total_pages': puntuaciones.pages,
        'total_results': puntuaciones.total
    }), 200

@app.route('/puntuaciones/<string:nombre>', methods=['GET'])
@authenticate_token
def obtener_puntuaciones_por_nombre(nombre):
    # Parámetros opcionales para paginación
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 15)

    # Validación de los parámetros
    try:
        page = int(page)
        per_page = int(per_page)
    except ValueError:
        return jsonify({'error': 'Los parámetros de paginación deben ser enteros'}), 400

    # Obtener el jugador por nombre
    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'mensaje': 'Jugador no encontrado'}), 404

    # Subconsulta para verificar si existe una relación de amistad
    amistad_subquery = db.session.query(Amistad.id).filter(
        ((Amistad.jugador_solicitante_id == jugador.id) & (Amistad.jugador_receptor_id == request.user_id)) |
        ((Amistad.jugador_receptor_id == jugador.id) & (Amistad.jugador_solicitante_id == request.user_id)),
        Amistad.estado == 'aceptado'
    ).exists()

    # Obtener el nivel de privacidad del jugador
    privacidad = Privacidad.query.filter_by(jugador_id=jugador.id).first()
    if not privacidad:
        return jsonify({'mensaje': 'Configuración de privacidad no encontrada'}), 404
    print(f"Privacidad del jugador: {privacidad.nivel_de_privacidad}")
    # Construir el filtro de privacidad
    if privacidad.nivel_de_privacidad == NivelPrivacidad.privado:
        return jsonify({'mensaje': 'El jugador tiene la privacidad configurada como privada'}), 403
    elif privacidad.nivel_de_privacidad == NivelPrivacidad.publico:
        # Obtener las puntuaciones asociadas al jugador con paginación
        puntuaciones = Puntuacion.query.filter_by(jugador_id=jugador.id).paginate(page=page, per_page=per_page)
    elif privacidad.nivel_de_privacidad == NivelPrivacidad.amigos:
        # Filtrar puntuaciones solo si la amistad es aceptada
        puntuaciones = Puntuacion.query.join(Jugadores) \
            .join(Privacidad) \
            .filter(
                Puntuacion.jugador_id == jugador.id,
                ((Privacidad.nivel_de_privacidad == 'publico') | 
                 ((Privacidad.nivel_de_privacidad == 'amigos') & amistad_subquery))
            ).paginate(page=page, per_page=per_page)
    else:
        return jsonify({'mensaje': 'El jugador tiene la privacidad configurada como privada'}), 403

    # Si no hay puntuaciones
    if not puntuaciones.items:
        return jsonify({'mensaje': 'No se encontraron puntuaciones para el usuario especificado'}), 404

    # Formatear los resultados en JSON
    resultado = [{'id': p.id, 'nombre': jugador.nombre, 'valor': p.valor} for p in puntuaciones.items]

    # Devolver los datos con información de paginación
    return jsonify({
        'puntuaciones': resultado,
        'page': puntuaciones.page,
        'per_page': puntuaciones.per_page,
        'total_pages': puntuaciones.pages,
        'total_results': puntuaciones.total
    }), 200








@app.route('/historico/<string:nombre>', methods=['GET'])
@authenticate_token
def get_historico_by_nombre(nombre):
    # Paginación
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))

    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    pagination = PuntuacionHistorico.query \
        .filter_by(jugador_id=jugador.id) \
        .order_by(PuntuacionHistorico.fecha_registro.desc()) \
        .paginate(page=page, per_page=per_page)

    items = [
        {
            'id': ph.id,
            'valor': ph.valor,
            'fecha_registro': ph.fecha_registro.isoformat()
        }
        for ph in pagination.items
    ]

    return jsonify({
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre},
        'historico': items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total_pages': pagination.pages,
        'total_results': pagination.total
    }), 200


@app.route('/historico', methods=['POST'])
@authenticate_token
def agregar_historico():
    data = request.get_json()
    nombre = data.get('nombre')
    valor = data.get('valor')

    if not nombre or valor is None:
        return jsonify({'error': 'Nombre y valor obligatorios'}), 400

    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    try:
        valor = int(valor)
    except ValueError:
        return jsonify({'error': 'Valor debe ser entero'}), 400

    nuevo = PuntuacionHistorico(valor=valor, jugador_id=jugador.id)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        'id': nuevo.id,
        'valor': nuevo.valor,
        'fecha_registro': nuevo.fecha_registro.isoformat(),
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre}
    }), 201


@app.route('/logros/nuevo', methods=['POST'])
@authenticate_token2(required_role='admin')
def crear_logro():
    """
    Crea un nuevo logro en la tabla 'logros'.
    Requiere rol 'admin'.
    """
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')

    # Validación de campos obligatorios
    if not nombre or not descripcion:
        return jsonify({'error': 'Nombre y descripción obligatorios'}), 400

    # Verificar duplicados
    existe = Logros.query.filter_by(nombre=nombre).first()
    if existe:
        return jsonify({'error': 'Ya existe un logro con ese nombre'}), 409

    try:
        nuevo_logro = Logros(nombre=nombre, descripcion=descripcion)
        db.session.add(nuevo_logro)
        db.session.commit()
        return jsonify({
            'id': nuevo_logro.id,
            'nombre': nuevo_logro.nombre,
            'descripcion': nuevo_logro.descripcion
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear logro', 'detalle': str(e)}), 500


@app.route('/logros/<string:nombre>', methods=['GET'])
@authenticate_token
def get_logros_by_nombre(nombre):
    """
    Funcion para obtener todos los logros obtenidos por el jugador.
    """
    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    items = [
        {
            'id': lj.id,
            'logro_id': lj.logro_id,
            'nombre_logro': lj.logro.nombre,
            'descripcion': lj.logro.descripcion,
            'fecha_obtenido': lj.fecha_obtenido.isoformat()
        }
        for lj in jugador.logros_jugados
    ]

    return jsonify({
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre},
        'logros': items
    }), 200


@app.route('/logros', methods=['POST'])
@authenticate_token
def agregar_logro_jugador():
    """
    Agregar un logro de la tabla de logros al jugador creando una 
    relacion entre ambos.
    """
    data = request.get_json()
    nombre = data.get('nombre')       # nombre del jugador
    logro_id = data.get('logro_id')   # id del logro a asociar

    if not nombre or not logro_id:
        return jsonify({'error': 'Nombre y logro_id obligatorios'}), 400

    jugador = Jugadores.query.filter_by(nombre=nombre).first()
    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    logro = Logros.query.get(logro_id)
    if not logro:
        return jsonify({'error': 'Logro no existe'}), 404

    # Verificar si ya tiene el logro
    ya_tiene_logro = LogroJugador.query.filter_by(
        jugador_id=jugador.id, logro_id=logro_id
    ).first()

    if ya_tiene_logro:
        return jsonify({
            'mensaje': 'El jugador ya tiene este logro',
            'jugador': {'id': jugador.id, 'nombre': jugador.nombre},
            'logro': {'id': logro.id, 'nombre': logro.nombre}
        }), 200  # o 409 si prefieres indicar conflicto

    nueva_rel = LogroJugador(
        jugador_id=jugador.id,
        logro_id=logro_id,
        fecha_obtenido=datetime.utcnow()
    )
    db.session.add(nueva_rel)
    db.session.commit()

    return jsonify({
        'id': nueva_rel.id,
        'jugador': {'id': jugador.id, 'nombre': jugador.nombre},
        'logro': {'id': logro.id, 'nombre': logro.nombre},
        'fecha_obtenido': nueva_rel.fecha_obtenido.isoformat()
    }), 201

@app.route('/privacidad/<int:jugador_id>', methods=['GET'])
def obtener_privacidad(jugador_id):
    try:
        # Obtener el nivel de privacidad del jugador
        privacidad = Privacidad.query.filter_by(jugador_id=jugador_id).first()

        if privacidad:
            return jsonify({
                'jugador_id': privacidad.jugador_id,
                'nivel_de_privacidad': privacidad.nivel_de_privacidad.value
            }), 200
        else:
            return jsonify({'message': 'Privacidad no encontrada para el jugador'}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/privacidad', methods=['POST'])
def crear_privacidad():
    try:
        data = request.get_json()
        jugador_id = data.get('jugador_id')
        nivel_de_privacidad = data.get('nivel_de_privacidad')

        # Validación de datos
        if not jugador_id or not nivel_de_privacidad:
            return jsonify({'message': 'Faltan parámetros requeridos'}), 400

        jugador = Jugadores.query.filter_by(id=jugador_id).first()
        if not jugador:
            return jsonify({'message': 'Jugador no encontrado'}), 404
        
        if Privacidad.query.filter_by(jugador_id=jugador_id).first():
            return jsonify({'message': 'Privacidad ya existe para este jugador'}), 400

        # Crear un nuevo registro de privacidad
        nueva_privacidad = Privacidad(jugador_id=jugador_id, nivel_de_privacidad=NivelPrivacidad[nivel_de_privacidad])
        db.session.add(nueva_privacidad)
        db.session.commit()

        return jsonify({
            'message': 'Privacidad creada correctamente',
            'jugador_id': nueva_privacidad.jugador_id,
            'nivel_de_privacidad': nueva_privacidad.nivel_de_privacidad.value
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/privacidad/<int:jugador_id>', methods=['PUT'])
def actualizar_privacidad(jugador_id):
    try:
        data = request.get_json()
        nivel_de_privacidad = data.get('nivel_de_privacidad')

        # Validación de datos
        if not nivel_de_privacidad:
            return jsonify({'message': 'Falta el parámetro nivel_de_privacidad'}), 400
        
        jugador = Jugadores.query.filter_by(id=jugador_id).first()
        if not jugador:
            return jsonify({'message': 'Jugador no encontrado'}), 404

        # Obtener el registro de privacidad existente para el jugador
        privacidad = Privacidad.query.filter_by(jugador_id=jugador_id).first()

        if privacidad:
            # Actualizar el nivel de privacidad
            privacidad.nivel_de_privacidad = NivelPrivacidad[nivel_de_privacidad]
            db.session.commit()

            return jsonify({
                'message': 'Privacidad actualizada correctamente',
                'jugador_id': privacidad.jugador_id,
                'nivel_de_privacidad': privacidad.nivel_de_privacidad.value
            }), 200
        else:
            return jsonify({'message': 'Privacidad no encontrada para el jugador'}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500






@app.route('/amistades/enviar_solicitud', methods=['POST'])
@authenticate_token  # Este decorador verifica el token y agrega el user_id al request
def enviar_solicitud():
    user_id = request.user_id  # ID del usuario autenticado proporcionado por el decorador
    datos = request.json

    jugador_solicitante = Jugadores.query.get(user_id)
    jugador_receptor = Jugadores.query.filter_by(nombre=datos['nombre_receptor']).first()

    if not jugador_solicitante or not jugador_receptor:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    # Verificar si ya existe una amistad entre ambos jugadores
    amistad_existente = Amistad.query.filter(
        ((Amistad.jugador_solicitante_id == jugador_solicitante.id) & 
         (Amistad.jugador_receptor_id == jugador_receptor.id)) |
        ((Amistad.jugador_solicitante_id == jugador_receptor.id) & 
         (Amistad.jugador_receptor_id == jugador_solicitante.id))
    ).first()

    if not amistad_existente:
        nueva_amistad = Amistad(
            jugador_solicitante_id=jugador_solicitante.id,
            jugador_receptor_id=jugador_receptor.id,
            estado='pendiente'
        )
        db.session.add(nueva_amistad)
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud enviada'}), 201
    else:
        return jsonify({'error': 'Ya existe una solicitud pendiente o son amigos'}), 400



@app.route('/amistades/aceptar_solicitud', methods=['POST'])
def aceptar_solicitud():
    datos = request.json
    jugador_receptor = Jugadores.query.get(datos['receptor_id'])
    jugador_solicitante = Jugadores.query.get(datos['solicitante_id'])

    if not jugador_solicitante or not jugador_receptor:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    amistad = Amistad.query.filter_by(
        jugador_solicitante_id=jugador_solicitante.id,
        jugador_receptor_id=jugador_receptor.id,
        estado='pendiente'
    ).first()

    if amistad:
        amistad.estado = 'aceptado'
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud aceptada'}), 200
    else:
        return jsonify({'error': 'No hay solicitud pendiente'}), 404



@app.route('/amistades/rechazar_solicitud', methods=['POST'])
def rechazar_solicitud():
    datos = request.json
    jugador_receptor = Jugadores.query.get(datos['receptor_id'])
    jugador_solicitante = Jugadores.query.get(datos['solicitante_id'])

    if not jugador_solicitante or not jugador_receptor:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    amistad = Amistad.query.filter_by(
        jugador_solicitante_id=jugador_solicitante.id,
        jugador_receptor_id=jugador_receptor.id,
        estado='pendiente'
    ).first()

    if amistad:
        amistad.estado = 'rechazado'
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud rechazada'}), 200
    else:
        return jsonify({'error': 'No hay solicitud pendiente para rechazar'}), 404


@app.route('/amistades/eliminar', methods=['DELETE'])
def eliminar_amistad():
    datos = request.json
    jugador_1 = Jugadores.query.get(datos['jugador_1_id'])
    jugador_2 = Jugadores.query.get(datos['jugador_2_id'])

    if not jugador_1 or not jugador_2:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    # Buscar la amistad entre ambos jugadores
    amistad = Amistad.query.filter(
        ((Amistad.jugador_solicitante_id == jugador_1.id) & 
         (Amistad.jugador_receptor_id == jugador_2.id)) |
        ((Amistad.jugador_solicitante_id == jugador_2.id) & 
         (Amistad.jugador_receptor_id == jugador_1.id))
    ).first()

    if amistad:
        db.session.delete(amistad)
        db.session.commit()
        return jsonify({'mensaje': 'Amistad eliminada'}), 200
    else:
        return jsonify({'error': 'No hay amistad entre estos jugadores'}), 404


@app.route('/amistades/obtener_pendientes', methods=['GET'])
@authenticate_token
def obtener_pendientes():
# Ahora obtenemos el user_id directamente desde request.user_id
    user_id = request.user_id
    jugador = Jugadores.query.get(user_id)

    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    amistades = Amistad.query.filter(
        ((Amistad.jugador_solicitante_id == jugador.id) | (Amistad.jugador_receptor_id == jugador.id)) &
        (Amistad.estado == 'pendiente')
    ).all()

    pendientes = []
    for amistad in amistades:
        if amistad.jugador_solicitante_id != jugador.id:
            pendientes.append({
                'nombre': amistad.solicitante.nombre,
                'solicitante_id': amistad.jugador_solicitante_id,
                'receptor_id': jugador.id
            })

        #Descomentar para mostrar solicitudes enviadas (TODO: Mostrar "Pendiente" en vez de botones "Aceptar" "Rechazar")
        #else:
        #    pendientes.append({
        #        'nombre': amistad.solicitante.nombre
        #    })

    return jsonify({'pendientes': pendientes}), 200


@app.route('/amistades/obtener_amigos', methods=['GET'])
@authenticate_token
def obtener_amigos():
    # Obtener el user_id desde request.user_id
    user_id = request.user_id
    jugador = Jugadores.query.get(user_id)

    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    # Filtrar las amistades en las que el jugador participa y cuyo estado es 'aceptado'
    amistades = Amistad.query.filter(
        ((Amistad.jugador_solicitante_id == jugador.id) | (Amistad.jugador_receptor_id == jugador.id)) &
        (Amistad.estado == 'aceptado')
    ).all()

    amigos = []
    for amistad in amistades:
        if amistad.jugador_solicitante_id == jugador.id:
            amigos.append({
                'id': amistad.receptor.id,  # ID del amigo receptor
                'nombre': amistad.receptor.nombre
                })
        else:
            amigos.append({
                'id': amistad.solicitante.id,  # ID del amigo solicitante
                'nombre': amistad.solicitante.nombre
                })

    return jsonify({'amigos': amigos}), 200





@app.route('/jugadores/obtener_id', methods=['GET'])
def obtener_id_por_nombre():
    nombre = request.args.get('nombre')  # Obtiene el nombre del jugador desde los parámetros de la URL

    if not nombre:
        return jsonify({'error': 'El nombre es requerido'}), 400

    # Buscar al jugador por su nombre
    jugador = Jugadores.query.filter_by(nombre=nombre).first()

    if not jugador:
        return jsonify({'error': 'Jugador no encontrado'}), 404

    # Retornar el ID del jugador
    return jsonify({'id': jugador.id}), 200








@app.route('/puntuaciones/<string:nombre>', methods=['DELETE'])
@authenticate_token2(required_role='admin')
def eliminar_puntuaciones(nombre):
    try:
        # Buscar las puntuaciones del jugador
        puntuaciones = Puntuacion.query.filter_by(nombre=nombre).all()
        
        if not puntuaciones:
            return jsonify({'mensaje': 'El jugador no existe'}), 404
        
        # Eliminar las puntuaciones
        for puntuacion in puntuaciones:
            db.session.delete(puntuacion)
        db.session.commit()
        
        return jsonify({'mensaje': 'Todas las puntuaciones del jugador han sido eliminadas'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@app.route('/puntuaciones/limpiar', methods=['DELETE'])
@authenticate_token2(required_role='admin')
def limpiar_puntuaciones():
    try:
        db.session.query(Puntuacion).delete()
        db.session.commit()
        return jsonify({'mensaje': 'Puntuaciones eliminadas correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/jugadores/limpiar', methods=['DELETE'])
@authenticate_token2(required_role='admin')
def limpiar_jugadores():
    try:
        # Primero, eliminar las puntuaciones asociadas
        db.session.query(Puntuacion).delete()
        db.session.commit()

        db.session.query(Privacidad).delete()
        db.session.commit()

        db.session.query(Amistad).delete()
        db.session.commit()

        # Ahora eliminar los jugadores
        db.session.query(Jugadores).delete()
        db.session.commit()

        return jsonify({'mensaje': 'Jugadores y puntuaciones eliminados correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)




