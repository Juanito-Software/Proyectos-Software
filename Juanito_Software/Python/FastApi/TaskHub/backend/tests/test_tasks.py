"""CRUD de tareas, etiquetas many-to-many, filtros y aislamiento entre usuarios."""
import pytest


def crear_tarea(client, headers, titulo="Escribir tests", **extra):
    return client.post("/tasks/", json={"title": titulo, **extra}, headers=headers)


# ── Crear ─────────────────────────────────────────────────────────────────────

class TestCrearTarea:
    def test_devuelve_201_y_la_tarea_creada(self, client, auth_headers):
        r = crear_tarea(client, auth_headers, description="Cobertura de services")
        assert r.status_code == 201
        body = r.json()
        assert body["title"] == "Escribir tests"
        assert body["description"] == "Cobertura de services"
        assert body["completed"] is False
        assert body["tags"] == []

    def test_asigna_el_owner_al_usuario_autenticado(self, client, auth_headers):
        me = client.get("/tasks/", headers=auth_headers)
        creada = crear_tarea(client, auth_headers).json()
        assert isinstance(creada["owner_id"], int)
        # La tarea aparece en el listado del propio usuario
        assert creada["id"] in [t["id"] for t in client.get("/tasks/", headers=auth_headers).json()]
        assert me.status_code == 200

    def test_422_si_falta_el_titulo(self, client, auth_headers):
        assert client.post("/tasks/", json={"description": "x"}, headers=auth_headers).status_code == 422

    def test_401_sin_autenticar(self, client):
        assert client.post("/tasks/", json={"title": "x"}).status_code == 401


# ── Etiquetas ─────────────────────────────────────────────────────────────────

class TestEtiquetas:
    def test_crea_las_etiquetas_indicadas(self, client, auth_headers):
        r = crear_tarea(client, auth_headers, tag_names=["backend", "urgente"])
        assert {t["name"] for t in r.json()["tags"]} == {"backend", "urgente"}

    @pytest.mark.parametrize("entrada", ["BACKEND", "Backend", "bAcKeNd"])
    def test_normaliza_a_minusculas(self, client, auth_headers, entrada):
        r = crear_tarea(client, auth_headers, tag_names=[entrada])
        assert r.json()["tags"][0]["name"] == "backend"

    def test_reutiliza_la_etiqueta_existente_en_vez_de_duplicarla(self, client, auth_headers):
        primera = crear_tarea(client, auth_headers, "A", tag_names=["backend"]).json()
        segunda = crear_tarea(client, auth_headers, "B", tag_names=["BACKEND"]).json()
        # Mismo id de tag pese a diferir en mayúsculas: get_or_create funciona.
        assert primera["tags"][0]["id"] == segunda["tags"][0]["id"]

    def test_una_tarea_admite_varias_etiquetas(self, client, auth_headers):
        r = crear_tarea(client, auth_headers, tag_names=["a", "b", "c"])
        assert len(r.json()["tags"]) == 3


# ── Listar y filtrar ──────────────────────────────────────────────────────────

class TestListarTareas:
    def test_lista_vacia_para_un_usuario_nuevo(self, client, auth_headers):
        assert client.get("/tasks/", headers=auth_headers).json() == []

    def test_filtra_por_completed(self, client, auth_headers):
        a = crear_tarea(client, auth_headers, "Pendiente").json()
        b = crear_tarea(client, auth_headers, "Hecha").json()
        client.patch(f"/tasks/{b['id']}", json={"completed": True}, headers=auth_headers)

        pendientes = client.get("/tasks/?completed=false", headers=auth_headers).json()
        hechas = client.get("/tasks/?completed=true", headers=auth_headers).json()

        assert [t["id"] for t in pendientes] == [a["id"]]
        assert [t["id"] for t in hechas] == [b["id"]]

    def test_filtra_por_etiqueta_ignorando_mayusculas(self, client, auth_headers):
        con_tag = crear_tarea(client, auth_headers, "Con", tag_names=["backend"]).json()
        crear_tarea(client, auth_headers, "Sin", tag_names=["frontend"])

        r = client.get("/tasks/?tag=BACKEND", headers=auth_headers).json()
        assert [t["id"] for t in r] == [con_tag["id"]]

    def test_sin_filtros_devuelve_todas(self, client, auth_headers):
        crear_tarea(client, auth_headers, "A")
        crear_tarea(client, auth_headers, "B")
        assert len(client.get("/tasks/", headers=auth_headers).json()) == 2


# ── Aislamiento entre usuarios ────────────────────────────────────────────────

class TestAislamientoEntreUsuarios:
    """Lo más crítico: ningún usuario puede leer ni tocar tareas ajenas."""

    def test_el_listado_solo_muestra_las_propias(self, client, auth_headers, other_auth_headers):
        mia = crear_tarea(client, auth_headers, "Mía").json()
        crear_tarea(client, other_auth_headers, "Suya")

        listado = client.get("/tasks/", headers=auth_headers).json()
        assert [t["id"] for t in listado] == [mia["id"]]

    def test_404_al_leer_una_tarea_ajena(self, client, auth_headers, other_auth_headers):
        ajena = crear_tarea(client, other_auth_headers, "Suya").json()
        # 404 y no 403: no revelamos que el recurso existe.
        assert client.get(f"/tasks/{ajena['id']}", headers=auth_headers).status_code == 404

    def test_404_al_modificar_una_tarea_ajena(self, client, auth_headers, other_auth_headers):
        ajena = crear_tarea(client, other_auth_headers, "Suya").json()
        r = client.patch(f"/tasks/{ajena['id']}", json={"title": "hackeada"}, headers=auth_headers)
        assert r.status_code == 404

    def test_404_al_borrar_una_tarea_ajena(self, client, auth_headers, other_auth_headers):
        ajena = crear_tarea(client, other_auth_headers, "Suya").json()
        assert client.delete(f"/tasks/{ajena['id']}", headers=auth_headers).status_code == 404
        # Y sigue existiendo para su dueño
        assert client.get(f"/tasks/{ajena['id']}", headers=other_auth_headers).status_code == 200


# ── Actualizar ────────────────────────────────────────────────────────────────

class TestActualizarTarea:
    def test_actualiza_solo_los_campos_enviados(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers, "Original", description="Desc original").json()

        r = client.patch(f"/tasks/{tarea['id']}", json={"title": "Nuevo"}, headers=auth_headers)

        assert r.json()["title"] == "Nuevo"
        assert r.json()["description"] == "Desc original"  # intacta (exclude_unset)

    def test_marca_como_completada(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers).json()
        r = client.patch(f"/tasks/{tarea['id']}", json={"completed": True}, headers=auth_headers)
        assert r.json()["completed"] is True

    def test_reemplaza_las_etiquetas_por_completo(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers, tag_names=["vieja"]).json()
        r = client.patch(f"/tasks/{tarea['id']}", json={"tag_names": ["nueva"]}, headers=auth_headers)
        assert {t["name"] for t in r.json()["tags"]} == {"nueva"}

    def test_lista_vacia_de_etiquetas_las_elimina_todas(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers, tag_names=["a", "b"]).json()
        r = client.patch(f"/tasks/{tarea['id']}", json={"tag_names": []}, headers=auth_headers)
        assert r.json()["tags"] == []

    def test_no_tocar_tag_names_conserva_las_etiquetas(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers, tag_names=["backend"]).json()
        r = client.patch(f"/tasks/{tarea['id']}", json={"title": "Otro"}, headers=auth_headers)
        assert {t["name"] for t in r.json()["tags"]} == {"backend"}

    def test_actualiza_el_campo_updated_at(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers).json()
        r = client.patch(f"/tasks/{tarea['id']}", json={"title": "Nuevo"}, headers=auth_headers)
        assert r.json()["updated_at"] >= tarea["updated_at"]

    def test_404_si_la_tarea_no_existe(self, client, auth_headers):
        assert client.patch("/tasks/9999", json={"title": "x"}, headers=auth_headers).status_code == 404


# ── Borrar ────────────────────────────────────────────────────────────────────

class TestBorrarTarea:
    def test_devuelve_204_y_deja_de_ser_accesible(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers).json()

        assert client.delete(f"/tasks/{tarea['id']}", headers=auth_headers).status_code == 204
        assert client.get(f"/tasks/{tarea['id']}", headers=auth_headers).status_code == 404

    def test_404_si_la_tarea_no_existe(self, client, auth_headers):
        assert client.delete("/tasks/9999", headers=auth_headers).status_code == 404

    def test_borrar_dos_veces_devuelve_404_la_segunda(self, client, auth_headers):
        tarea = crear_tarea(client, auth_headers).json()
        client.delete(f"/tasks/{tarea['id']}", headers=auth_headers)
        assert client.delete(f"/tasks/{tarea['id']}", headers=auth_headers).status_code == 404
