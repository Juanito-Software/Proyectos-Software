//! Tests de integración del crawler sobre archivos reales en disco.
//!
//! Ejercitan `index_directory` de punta a punta: extensión de texto
//! reconocida, subdirectorios, profundidad máxima, archivos vacíos,
//! directorio inexistente y codificación con la que no es UTF-8.

mod comun;

use std::path::Path;

use motor_indexado::index_directory;

use comun::{directorio_temporal, escribir_archivo, limpiar};

#[test]
fn indexa_archivos_de_texto_de_un_directorio() {
    let dir = directorio_temporal("crawler_basico");
    escribir_archivo(&dir, "a.txt", "hola mundo");
    escribir_archivo(&dir, "b.md", "hola rust");

    let indice = index_directory(&dir, None);

    assert_eq!(indice.doc_count(), 2);
    assert_eq!(indice.term_count(), 3);
    let postings = indice.postings("hola").expect("término presente");
    assert_eq!(postings.len(), 2);

    limpiar(&dir);
}

#[test]
fn ignora_extensiones_que_no_son_de_texto() {
    let dir = directorio_temporal("crawler_extensiones");
    escribir_archivo(&dir, "a.txt", "hola");
    escribir_archivo(&dir, "foto.png", "hola");
    escribir_archivo(&dir, "sin_extension", "hola");

    let indice = index_directory(&dir, None);

    assert_eq!(indice.doc_count(), 1);
    assert_eq!(indice.term_count(), 1);

    limpiar(&dir);
}

#[test]
fn recorre_subdirectorios() {
    let dir = directorio_temporal("crawler_recursivo");
    escribir_archivo(&dir, "raiz.txt", "hola raiz");
    escribir_archivo(&dir, "nivel1/interior.md", "hola interior");
    escribir_archivo(&dir, "nivel1/nivel2/fondo.rs", "hola fondo");

    let indice = index_directory(&dir, None);

    assert_eq!(indice.doc_count(), 3);
    let postings = indice.postings("hola").expect("término presente");
    assert_eq!(postings.len(), 3);

    limpiar(&dir);
}

#[test]
fn respeta_la_profundidad_maxima() {
    let dir = directorio_temporal("crawler_profundidad");
    escribir_archivo(&dir, "raiz.txt", "hola raiz");
    escribir_archivo(&dir, "nivel1/interior.md", "hola interior");
    escribir_archivo(&dir, "nivel1/nivel2/fondo.rs", "hola fondo");

    // WalkDir cuenta la raíz como profundidad 0: con 1 solo entran los archivos
    // directos de la raíz; con 2, también los del primer subdirectorio.
    let solo_raiz = index_directory(&dir, Some(1));
    let un_nivel = index_directory(&dir, Some(2));

    assert_eq!(solo_raiz.doc_count(), 1);
    assert_eq!(un_nivel.doc_count(), 2);

    limpiar(&dir);
}

#[test]
fn ignora_archivos_vacios() {
    let dir = directorio_temporal("crawler_vacio");
    escribir_archivo(&dir, "vacio.txt", "");
    escribir_archivo(&dir, "espacios.txt", "   \n  ");

    let indice = index_directory(&dir, None);

    assert_eq!(indice.doc_count(), 0);
    assert_eq!(indice.term_count(), 0);

    limpiar(&dir);
}

#[test]
fn directorio_inexistente_devuelve_indice_vacio() {
    let indice = index_directory(Path::new("no/existe/esto"), None);
    assert_eq!(indice.doc_count(), 0);
}

#[test]
fn decodifica_archivos_que_no_son_utf8() {
    // "café" en Windows-1252: el byte 0xE9 es la 'é' con acento agudo.
    let dir = directorio_temporal("crawler_encoding");
    let bytes = [0x63, 0x61, 0x66, 0xE9];
    std::fs::write(dir.join("cafe.txt"), bytes).expect("no se puede escribir el archivo");

    let indice = index_directory(&dir, None);

    assert_eq!(indice.doc_count(), 1);
    let postings = indice.postings("café").expect("término presente");
    assert_eq!(postings.len(), 1);

    limpiar(&dir);
}