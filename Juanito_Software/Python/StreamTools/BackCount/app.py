from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
from urllib.parse import quote
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Almacenamiento en memoria de los temporizadores
timers = {}

@app.route('/')
def index():
    """Página principal de configuración"""
    return render_template('index.html')

@app.route('/timer')
def timer():
    """Página del temporizador visual"""
    return render_template('timer.html')

@app.route('/api/config', methods=['POST'])
def save_config():
    """Guardar configuración del temporizador"""
    config = request.json
    
    # Calcular tiempo de finalización
    hours = int(config.get('hours', 0))
    minutes = int(config.get('minutes', 0))
    seconds = int(config.get('seconds', 0))
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    end_time = datetime.now() + timedelta(seconds=total_seconds)
    
    timer_id = secrets.token_hex(8)
    timers[timer_id] = {
        'end_time': end_time.isoformat(),
        'config': config
    }
    
    config['timer_id'] = timer_id
    
    # Crear URL con parámetros para el temporizador (codificando caracteres especiales como #)
    text_color = quote(config.get('textColor', '#ffffff'))
    font_size = config.get('fontSize', 120)
    
    params = f"timer_id={timer_id}&textColor={text_color}&fontSize={font_size}"
    if config.get('text'):
        params += f"&text={quote(config['text'])}"
    
    config['timer_url'] = f"/timer?{params}"
    
    return jsonify(config)

@app.route('/api/timer/<timer_id>', methods=['GET'])
def get_timer_status(timer_id):
    """Obtener estado actual del temporizador"""
    if timer_id not in timers:
        return jsonify({'error': 'Timer not found'}), 404
    
    timer_data = timers[timer_id]
    end_time = datetime.fromisoformat(timer_data['end_time'])
    now = datetime.now()
    
    if now >= end_time:
        return jsonify({
            'active': False,
            'remaining': 0,
            'finished': True
        })
    
    remaining = (end_time - now).total_seconds()
    
    return jsonify({
        'active': True,
        'remaining': int(remaining),
        'finished': False
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CUENTA ATRÁS PERSONALIZADA PARA OBS")
    print("="*60)
    print("\nServidor iniciado en:")
    print("  - Local:  http://localhost:5000")
    print("  - Red:    http://0.0.0.0:5000")
    print("\nNota: Para OBS, usa la dirección IP de tu red local.")
    print("="*60 + "\n")
    
    # host='0.0.0.0' es intencionado: OBS necesita alcanzar el servidor desde
    # la red local. Por eso mismo debug debe estar desactivado: el depurador
    # de Werkzeug permitiría ejecutar código arbitrario a cualquiera en la LAN.
    app.run(host='0.0.0.0', port=5000, debug=False)

