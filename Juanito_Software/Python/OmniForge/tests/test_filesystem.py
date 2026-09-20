"""Tests de las tools de sistema de archivos (operaciones sobre tmp_path).

Las tools de langchain no son llamables directamente: son StructuredTool y se
invocan con .invoke({"param": valor})."""
from tools.filesystem import read_file, write_file, list_dir, delete_file


class TestReadWrite:
    def test_escribir_y_leer_archivo(self, tmp_path):
        ruta = tmp_path / "foo.txt"
        resultado = write_file.invoke({"path": str(ruta), "content": "hola mundo"})
        assert resultado.startswith("OK:")
        assert read_file.invoke({"path": str(ruta)}) == "hola mundo"

    def test_write_crea_directorios_intermedios(self, tmp_path):
        ruta = tmp_path / "a" / "b" / "c.txt"
        write_file.invoke({"path": str(ruta), "content": "contenido"})
        assert ruta.exists()
        assert read_file.invoke({"path": str(ruta)}) == "contenido"

    def test_read_de_archivo_inexistente_devuelve_error(self, tmp_path):
        resultado = read_file.invoke({"path": str(tmp_path / "no_existe.txt")})
        assert "ERROR" in resultado
        assert "no encontrado" in resultado.lower()

    def test_read_de_directorio_devuelve_error(self, tmp_path):
        resultado = read_file.invoke({"path": str(tmp_path)})
        assert "ERROR" in resultado


class TestListDir:
    def test_lista_contenido_con_tipos(self, tmp_path):
        (tmp_path / "archivo.txt").write_text("x", encoding="utf-8")
        (tmp_path / "carpeta").mkdir()
        lista = list_dir.invoke({"path": str(tmp_path)})
        assert "FILE  archivo.txt" in lista
        assert "DIR" in lista and "carpeta" in lista

    def test_lista_directorio_vacio(self, tmp_path):
        assert list_dir.invoke({"path": str(tmp_path)}) == "(directorio vacío)"

    def test_lista_directorio_inexistente(self, tmp_path):
        resultado = list_dir.invoke({"path": str(tmp_path / "no_existe")})
        assert "ERROR" in resultado


class TestDelete:
    def test_elimina_archivo(self, tmp_path):
        ruta = tmp_path / "borrame.txt"
        ruta.write_text("x", encoding="utf-8")
        resultado = delete_file.invoke({"path": str(ruta)})
        assert resultado.startswith("OK:")
        assert not ruta.exists()

    def test_no_elimina_directorios(self, tmp_path):
        resultado = delete_file.invoke({"path": str(tmp_path)})
        assert "directorio" in resultado.lower()
        assert tmp_path.exists()

    def test_eliminar_inexistente_devuelve_error(self, tmp_path):
        resultado = delete_file.invoke({"path": str(tmp_path / "no_existe.txt")})
        assert "ERROR" in resultado