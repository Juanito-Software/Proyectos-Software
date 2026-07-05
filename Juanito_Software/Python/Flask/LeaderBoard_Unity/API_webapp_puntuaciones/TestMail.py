from flask import Flask, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'deadvalleygame@gmail.com'
app.config['MAIL_PASSWORD'] = 'jgvn mdyn vhrz mtvv'

mail = Mail(app)

@app.route('/test-email', methods=['POST'])
def test_email():
    data = request.get_json()
    email = data.get('email')
    try:
        msg = Message("Prueba", recipients=[email], body="Hola mundo desde Flask")
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
