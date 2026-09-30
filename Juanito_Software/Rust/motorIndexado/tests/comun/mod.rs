//! Utilidades compartidas para los tests de integración.
//!
//! Cada test integración del motor necesita crear archivos en disco sin pisar
//! los de otros tests. Se usa un directorio temporal distinto por test, con
//! nombre único, y se borra al terminar (mejor esfuerzo).

use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

static CONTADOR: AtomicU64 = AtomicU64::new(0);

/// Crea un directorio temporal único para un test.
pub fn directorio_temporal(nombre: &str) -> PathBuf {
    let base = std::env::temp_dir().join("motor_indexado_test");
    let id = CONTADOR.fetch_add(1, Ordering::SeqCst);
    let dir = base.join(format!("{}_{}_{}", nombre, std::process::id(), id));
    fs::create_dir_all(&dir).expect("no se puede crear el directorio temporal");
    dir
}

/// Escribe un archivo con el contenido dado dentro de un directorio,
/// creando los subdirectorios intermedios que hagan falta.
pub fn escribir_archivo(dir: &Path, nombre: &str, contenido: &str) {
    let ruta = dir.join(nombre);
    if let Some(padre) = ruta.parent() {
        fs::create_dir_all(padre).expect("no se puede crear el directorio padre");
    }
    fs::write(ruta, contenido).expect("no se puede escribir el archivo");
}

/// Borra el directorio temporal (mejor esfuerzo, para no dejar basura).
pub fn limpiar(dir: &Path) {
    let _ = fs::remove_dir_all(dir);
}