import os

from flask import Flask, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']

mail = Mail(app)

@app.route('/test-email', methods=['POST'])
def test_email():
    data = request.get_json()
    email = data.get('email')
    try:
        msg = Message("Prueba", recipients=[email], body="Hola mundo desde Flask")
        mail.send(msg)
        return jsonify({'success': True})
    except Exception:
        # El detalle del error va al log del servidor, no a la respuesta. Un
        # fallo de SMTP menciona el servidor, el puerto y a veces el usuario con
        # el que se autentica: informacion que ayuda a quien ataca y no al
        # usuario legitimo, que solo necesita saber que no se pudo enviar.
        app.logger.exception("Fallo al enviar el correo de prueba")
        return jsonify({'error': 'No se pudo enviar el correo.'}), 500

if __name__ == '__main__':
    # Sin debug: el depurador de Werkzeug permite ejecutar código arbitrario.
    app.run(debug=False)
