"""
Fixtures compartidas.

Cada test corre contra una base SQLite en memoria propia: no toca la BD real,
no hay estado compartido entre tests y no hace falta limpiar nada.
"""
import os

# Debe ejecutarse ANTES de importar app.config, que valida el entorno al importarse.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    # StaticPool + una sola conexión: sin él, cada sesión abriría una BD
    # en memoria distinta y las tablas creadas aquí no se verían.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """TestClient con get_db sustituido por la sesión en memoria."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _register_and_login(client, username: str, email: str, password: str = "secreto123"):
    client.post("/auth/register", json={"email": email, "username": username, "password": password})
    resp = client.post("/auth/token", data={"username": username, "password": password})
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(client):
    """Cabecera Authorization de un usuario ya registrado."""
    token = _register_and_login(client, "juan", "juan@test.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def other_auth_headers(client):
    """Segundo usuario, para comprobar el aislamiento de datos entre cuentas."""
    token = _register_and_login(client, "ana", "ana@test.com")
    return {"Authorization": f"Bearer {token}"}
