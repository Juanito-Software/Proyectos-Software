from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from datetime import datetime

db = SQLAlchemy()

class Puntuacion(db.Model):
    __tablename__ = 'puntuaciones'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    valor = db.Column(db.Integer, nullable=False)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)  # Clave foránea sin "unique"

    # Relación con Jugadores para acceder al nombre
    jugador = db.relationship('Jugadores', lazy='joined')  # Lazy 'joined' para cargar datos relacionados directamente

    def __repr__(self):
        return f'<Puntuacion ID: {self.id}, Valor: {self.valor}, Jugador: {self.jugador.nombre}>'


class Jugadores(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nombre = db.Column(db.String(12), nullable=False, unique=True)  # Único para cada jugador
    email = db.Column(db.String(50), unique=True)
    numtelefono = db.Column(db.String(9), unique=True)
    password = db.Column(db.String(256))
    rol = db.Column(db.String(20), default='jugador')  # Campo de rol, por defecto 'jugador'
    refresh_token = db.Column(db.Text)  # Nuevo campo para almacenar el Refresh Token

    # Relaciones para solicitudes de amistad
    amistades_enviadas = db.relationship('Amistad', foreign_keys='Amistad.jugador_solicitante_id', back_populates='solicitante', cascade='all, delete-orphan')
    amistades_recibidas = db.relationship('Amistad', foreign_keys='Amistad.jugador_receptor_id', back_populates='receptor', cascade='all, delete-orphan')

    # Relacion para logros
    logros_jugados = db.relationship('LogroJugador', back_populates='jugador', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Jugador ID: {self.id}, Nombre: {self.nombre}>'


class NivelPrivacidad(PyEnum):
    publico = 'publico'
    privado = 'privado'
    amigos = 'amigos'

class Privacidad(db.Model):
    __tablename__ = 'privacidad'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nivel_de_privacidad = db.Column(db.Enum(NivelPrivacidad), nullable=False, default=NivelPrivacidad.publico)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)

    # Relación con Jugadores
    jugador = db.relationship('Jugadores', backref='privacidad', uselist=False, lazy='joined')

    def __repr__(self):
        return f'<Privacidad ID: {self.id}, Nivel: {self.nivel_de_privacidad}, Jugador: {self.jugador.nombre}>'
    


class Amistad(db.Model):
    __tablename__ = 'amistades'
    id = db.Column(db.Integer, primary_key=True)
    jugador_solicitante_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)
    jugador_receptor_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # Estados: 'pendiente', 'aceptado', 'rechazado'

    # Relaciones con el modelo Jugador
    solicitante = db.relationship('Jugadores', foreign_keys=[jugador_solicitante_id], back_populates='amistades_enviadas')
    receptor = db.relationship('Jugadores', foreign_keys=[jugador_receptor_id], back_populates='amistades_recibidas')


class Logros(db.Model):
    __tablename__ = 'logros'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    ganadores = db.relationship('LogroJugador', back_populates='logro', lazy=True)

class LogroJugador(db.Model):
    __tablename__ = 'logros_jugadores'
    id = db.Column(db.Integer, primary_key=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id', ondelete='CASCADE'), nullable=False)
    logro_id = db.Column(db.Integer, db.ForeignKey('logros.id',    ondelete='CASCADE'), nullable=False)
    fecha_obtenido = db.Column(db.DateTime, default=datetime.utcnow,     nullable=False)
    jugador = db.relationship('Jugadores',    back_populates='logros_jugados', lazy=True)
    logro = db.relationship('Logros',       back_populates='ganadores',      lazy=True)

    def __repr__(self):
        return f'<Jugador ID: {self.jugador_id}, logro: {self.logro_id}>'

class PuntuacionHistorico(db.Model):
    __tablename__ = 'puntuaciones_historico'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id', ondelete='CASCADE'),nullable=False)
    jugador = db.relationship('Jugadores', backref='puntuaciones_historico', lazy='joined')

    def __repr__(self):
        return f'<Jugador ID: {self.jugador_id}, valor: {self.valor}>'