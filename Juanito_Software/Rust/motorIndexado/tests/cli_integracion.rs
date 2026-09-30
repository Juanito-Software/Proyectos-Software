//! Tests de integración de la CLI real (el binario motor-indexado).
//!
//! Se ejecuta el binario compilado con `env!("CARGO_BIN_EXE_...")`, no el
//! código de `main` copiado. De la ruta del binario en el test se deduce que
//! estos tests corren a la vez que esto, y en las mismas condiciones.

mod comun;

use std::process::Command;

use comun::{directorio_temporal, escribir_archivo, limpiar};

fn binario() -> Command {
    Command::new(env!("CARGO_BIN_EXE_motor-indexado"))
}

fn salida_stdout(salida: &std::process::Output) -> String {
    String::from_utf8_lossy(&salida.stdout).into_owned()
}

#[test]
fn index_guarda_el_indice_en_disco() {
    let dir = directorio_temporal("cli_index");
    escribir_archivo(&dir, "a.txt", "hola mundo");

    let salida = binario()
        .args(["index", dir.to_str().unwrap()])
        .arg("--output")
        .arg(dir.join("indice.json"))
        .output()
        .expect("ejecutar el binario");

    assert!(salida.status.success());
    let texto = salida_stdout(&salida);
    assert!(texto.contains("Documentos: 1"));
    assert!(dir.join("indice.json").exists());

    limpiar(&dir);
}

#[test]
fn search_devuelve_resultados_de_un_indice_guardado() {
    let dir = directorio_temporal("cli_search");
    escribir_archivo(&dir, "a.txt", "hola mundo");
    let indice = dir.join("indice.json");

    let indexado = binario()
        .args(["index", dir.to_str().unwrap()])
        .arg("--output")
        .arg(&indice)
        .output()
        .expect("ejecutar index");
    assert!(indexado.status.success());

    let salida = binario()
        .args(["search", "mundo"])
        .arg("--index")
        .arg(&indice)
        .output()
        .expect("ejecutar search");

    assert!(salida.status.success());
    let texto = salida_stdout(&salida);
    assert!(texto.contains("a.txt"));
    assert!(texto.contains("score: 1"));

    limpiar(&dir);
}

#[test]
fn run_indexa_y_busca_en_una_sola_pasada() {
    let dir = directorio_temporal("cli_run");
    escribir_archivo(&dir, "a.txt", "hola mundo");

    let salida = binario()
        .args(["run", dir.to_str().unwrap(), "mundo"])
        .output()
        .expect("ejecutar run");

    assert!(salida.status.success());
    let texto = salida_stdout(&salida);
    assert!(texto.contains("a.txt"));

    limpiar(&dir);
}

#[test]
fn search_sin_resultados_avisa_y_sale_en_verde() {
    let dir = directorio_temporal("cli_sin_resultados");
    escribir_archivo(&dir, "a.txt", "hola mundo");
    let indice = dir.join("indice.json");

    let indexado = binario()
        .args(["index", dir.to_str().unwrap()])
        .arg("--output")
        .arg(&indice)
        .output()
        .expect("ejecutar index");
    assert!(indexado.status.success());

    let salida = binario()
        .args(["search", "inexistente"])
        .arg("--index")
        .arg(&indice)
        .output()
        .expect("ejecutar search");

    assert!(salida.status.success());
    let texto = salida_stdout(&salida);
    assert!(texto.contains("No se encontraron resultados."));

    limpiar(&dir);
}