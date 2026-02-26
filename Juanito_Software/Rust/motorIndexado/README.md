# Motor de indexación y búsqueda local

Un **indexador de archivos local** en Rust: recorre el disco, indexa texto, construye un **índice invertido** y permite **búsquedas ultrarrápidas**. Interfaz CLI y, opcionalmente, API HTTP ligera.

Concepto similar en miniatura a **Elasticsearch** o **ripgrep** (pero con índice persistente y búsqueda por términos).

## Por qué Rust

- **Memoria segura** sin GC (ownership, borrowing, lifetimes).
- **Rendimiento** cercano a C++.
- **Concurrencia real** con Rayon (indexación paralela) y, con la feature `api`, async con Tokio/Axum.
- Ideal para procesamiento intensivo y sistemas de bajo nivel.

## Requisitos

- [Rust](https://www.rust-lang.org/) (toolchain estable, p. ej. 1.70+).

## Compilación

```bash
cargo build --release
```

Con soporte para API HTTP:

```bash
cargo build --release --features api
```

## Uso (CLI)

### 1. Indexar un directorio

Crea el índice y lo guarda en `indice.json` (o en el archivo que indiques):

```bash
cargo run -- index ./mi_carpeta
cargo run -- index ./proyecto -o indice_proyecto.json
cargo run -- index ./proyecto --depth 3   # solo 3 niveles de carpetas
```

### 2. Buscar en el índice

```bash
cargo run -- search "palabras a buscar"
cargo run -- search "rust ownership" -i indice_proyecto.json --limit 10
```

### 3. Indexar y buscar en una sola pasada (sin guardar índice)

```bash
cargo run -- run ./mi_carpeta "consulta"
```

### 4. Servir API HTTP (solo si compilaste con `--features api`)

Primero genera un índice, luego:

```bash
cargo run --features api -- serve --index indice.json --bind 127.0.0.1:3030
```

- **GET** `http://127.0.0.1:3030/search?q=consulta&limit=20`  
- Respuesta JSON con `results`: `path`, `score`, `matches`.

## Extensiones indexadas

Se indexan archivos de texto por extensión, por ejemplo:  
`txt`, `md`, `rs`, `py`, `js`, `ts`, `json`, `toml`, `yml`, `html`, `css`, `xml`, `csv`, `log`, `sql`, `sh`, `bat`, `ps1`.

## Estructura del proyecto

| Módulo      | Descripción                                      |
|------------|---------------------------------------------------|
| `tokenizer`| Normaliza texto (minúsculas) y tokeniza.          |
| `index`    | Índice invertido: término → (archivo → frecuencia). |
| `crawler`  | Recorre directorios con `walkdir`, indexa en paralelo con Rayon. |
| `search`   | Búsqueda multi-término y ranking por score.      |
| `api`      | (Opcional) API HTTP con Axum.                    |

## Tests

```bash
cargo test
```

## Licencia

MIT.

Cómo usarlo

# Indexar
cargo run -- index . -o indice.json

# Buscar
cargo run -- search "rust ownership" --limit 10

# Con API HTTP
cargo build --release --features api
cargo run --features api -- serve --bind 127.0.0.1:3030
