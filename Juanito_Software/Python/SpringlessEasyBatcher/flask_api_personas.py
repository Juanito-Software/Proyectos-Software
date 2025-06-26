# Copyright (C) 2025 Juanito Software
#
# Este programa está protegido por una Licencia de Uso No Comercial.
# Puedes utilizarlo y compartirlo de forma gratuita, siempre que no se modifique
# y se incluya este aviso completo.
#
# Queda prohibido su uso con fines comerciales, así como su modificación,
# ingeniería inversa o redistribución alterada.
#
# Este software se proporciona “tal cual”, sin garantía de ningún tipo, ya sea
# expresa o implícita, incluyendo, pero no limitado a, garantías de comerciabilidad
# o idoneidad para un propósito particular.
#
# Para más detalles, consulta el archivo LICENSE.txt incluido con este programa
# o contacta a bernaldezperedaj@gmail.com.


# flask_api_personas.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)

# Conexión a PostgreSQL (con el password escapado)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://admin:P%40ssw0rd1%3F@localhost:5432/SpringlessEasyBatcher'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Persona (usa el mismo esquema que tu CSV y BD)
class Persona(db.Model):
    __tablename__ = 'persona_lectura'

    ID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String)
    Apellido = db.Column(db.String)
    Edad = db.Column(db.Integer)
    Email = db.Column(db.String)
    Teléfono = db.Column(db.String)
    Ciudad = db.Column(db.String)
    País = db.Column(db.String)
    Dirección = db.Column(db.String)
    Fecha_Registro = db.Column(db.String)

    def to_dict(self):
        return {
            "ID": self.ID,
            "Nombre": self.Nombre,
            "Apellido": self.Apellido,
            "Edad": self.Edad,
            "Email": self.Email,
            "Teléfono": self.Teléfono,
            "Ciudad": self.Ciudad,
            "País": self.País,
            "Dirección": self.Dirección,
            "Fecha_Registro": self.Fecha_Registro
        }




@app.route('/personas', methods=['POST'])
def add_persona():
    data = request.get_json()

    try:
        nueva = Persona(
            ID=data['ID'],
            Nombre=data['Nombre'],
            Apellido=data['Apellido'],
            Edad=data['Edad'],
            Email=data['Email'],
            Teléfono=data['Teléfono'],
            Ciudad=data['Ciudad'],
            País=data['País'],
            Dirección=data['Dirección'],
            Fecha_Registro=data['Fecha_Registro']
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"mensaje": "Persona añadida correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/personas', methods=['GET'])
def get_all_personas():
    personas = Persona.query.all()
    return jsonify([p.to_dict() for p in personas])


@app.route('/personas/<int:persona_id>', methods=['GET'])
def get_persona_by_id(persona_id):
    persona = Persona.query.get(persona_id)
    if persona:
        return jsonify(persona.to_dict())
    return jsonify({"error": "Persona no encontrada"}), 404


if __name__ == '__main__':
    app.run(debug=True)
