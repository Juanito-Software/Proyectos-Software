"""Tests de hashing, emisión/validación de JWT y endpoints de registro y login."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth import create_access_token, hash_password, verify_password
from app.config import settings


# ── Hashing ───────────────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_el_hash_nunca_es_la_password_en_claro(self):
        hashed = hash_password("secreto123")
        assert hashed != "secreto123"
        assert hashed.startswith("$2b$")

    def test_verify_acepta_la_password_correcta(self):
        assert verify_password("secreto123", hash_password("secreto123")) is True

    def test_verify_rechaza_una_password_incorrecta(self):
        assert verify_password("otra", hash_password("secreto123")) is False

    def test_dos_hashes_de_la_misma_password_difieren(self):
        # bcrypt genera un salt aleatorio por hash: dos usuarios con la misma
        # contraseña no comparten hash.
        assert hash_password("secreto123") != hash_password("secreto123")

    def test_verify_distingue_mayusculas(self):
        assert verify_password("Secreto123", hash_password("secreto123")) is False


# ── JWT ───────────────────────────────────────────────────────────────────────

class TestAccessToken:
    def test_incluye_sub_y_exp(self):
        payload = jwt.decode(
            create_access_token({"sub": "juan"}),
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["sub"] == "juan"
        assert "exp" in payload

    def test_caduca_segun_la_configuracion(self):
        # Se compara en UTC explícito: create_access_token usa datetime.utcnow(),
        # que devuelve un datetime naive, y .timestamp() sobre un naive lo
        # interpretaría como hora local y desplazaría el resultado.
        antes = datetime.now(timezone.utc)
        payload = jwt.decode(
            create_access_token({"sub": "juan"}),
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        esperado = antes + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert abs(payload["exp"] - esperado.timestamp()) < 5

    def test_no_valida_con_otro_secreto(self):
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                create_access_token({"sub": "juan"}),
                "secreto-del-atacante",
                algorithms=[settings.ALGORITHM],
            )


# ── POST /auth/register ───────────────────────────────────────────────────────

class TestRegister:
    def test_crea_el_usuario_y_devuelve_201(self, client):
        r = client.post("/auth/register", json={
            "email": "nuevo@test.com", "username": "nuevo", "password": "secreto123",
        })
        assert r.status_code == 201
        assert r.json()["username"] == "nuevo"
        assert r.json()["is_active"] is True

    def test_la_respuesta_no_expone_el_hash(self, client):
        r = client.post("/auth/register", json={
            "email": "nuevo@test.com", "username": "nuevo", "password": "secreto123",
        })
        body = r.json()
        assert "hashed_password" not in body
        assert "password" not in body

    def test_rechaza_email_duplicado(self, client):
        payload = {"email": "dup@test.com", "username": "uno", "password": "secreto123"}
        client.post("/auth/register", json=payload)
        r = client.post("/auth/register", json={**payload, "username": "dos"})
        assert r.status_code == 400
        assert "email" in r.json()["detail"].lower()

    def test_rechaza_username_duplicado(self, client):
        payload = {"email": "a@test.com", "username": "repetido", "password": "secreto123"}
        client.post("/auth/register", json=payload)
        r = client.post("/auth/register", json={**payload, "email": "b@test.com"})
        assert r.status_code == 400
        assert "username" in r.json()["detail"].lower()

    @pytest.mark.parametrize("email", ["sin-arroba", "@sin-usuario.com", "espacio @test.com", ""])
    def test_rechaza_emails_con_formato_invalido(self, client, email):
        r = client.post("/auth/register", json={
            "email": email, "username": "x", "password": "secreto123",
        })
        assert r.status_code == 422  # validación de Pydantic (EmailStr)


# ── POST /auth/token ──────────────────────────────────────────────────────────

class TestLogin:
    def test_devuelve_un_bearer_token_con_credenciales_correctas(self, client):
        client.post("/auth/register", json={
            "email": "juan@test.com", "username": "juan", "password": "secreto123",
        })
        r = client.post("/auth/token", data={"username": "juan", "password": "secreto123"})

        assert r.status_code == 200
        assert r.json()["token_type"] == "bearer"
        payload = jwt.decode(
            r.json()["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "juan"

    def test_401_si_el_usuario_no_existe(self, client):
        r = client.post("/auth/token", data={"username": "fantasma", "password": "x"})
        assert r.status_code == 401

    def test_401_si_la_password_es_incorrecta(self, client):
        client.post("/auth/register", json={
            "email": "juan@test.com", "username": "juan", "password": "secreto123",
        })
        r = client.post("/auth/token", data={"username": "juan", "password": "incorrecta"})
        assert r.status_code == 401

    def test_mismo_mensaje_para_usuario_inexistente_y_password_erronea(self, client):
        # Evita enumeración de usuarios: las dos respuestas deben ser idénticas.
        client.post("/auth/register", json={
            "email": "juan@test.com", "username": "juan", "password": "secreto123",
        })
        sin_usuario = client.post("/auth/token", data={"username": "nadie", "password": "x"})
        mala_pass = client.post("/auth/token", data={"username": "juan", "password": "x"})

        assert sin_usuario.status_code == mala_pass.status_code
        assert sin_usuario.json()["detail"] == mala_pass.json()["detail"]

    def test_incluye_la_cabecera_www_authenticate_en_el_401(self, client):
        r = client.post("/auth/token", data={"username": "fantasma", "password": "x"})
        assert r.headers.get("www-authenticate") == "Bearer"


# ── Protección de rutas ───────────────────────────────────────────────────────

class TestRutasProtegidas:
    def test_401_sin_cabecera_authorization(self, client):
        assert client.get("/tasks/").status_code == 401

    def test_401_con_token_con_firma_invalida(self, client):
        token = jwt.encode({"sub": "juan"}, "secreto-falso", algorithm="HS256")
        r = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_401_con_token_caducado(self, client):
        token = jwt.encode(
            {"sub": "juan", "exp": datetime.utcnow() - timedelta(minutes=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        r = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_401_si_el_token_no_lleva_sub(self, client):
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=30)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        r = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_401_si_el_sub_apunta_a_un_usuario_inexistente(self, client):
        token = create_access_token({"sub": "usuario-borrado"})
        r = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_401_con_token_sin_firmar_alg_none(self, client):
        # Confusión de algoritmos: get_current_user fija algorithms=[HS256],
        # así que un token con "alg": "none" debe rechazarse.
        token = jwt.encode({"sub": "juan"}, key="", algorithm="none")
        r = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401
