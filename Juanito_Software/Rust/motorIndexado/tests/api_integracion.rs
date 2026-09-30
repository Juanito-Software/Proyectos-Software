//! Tests de integración de la API HTTP (feature `api`).
//!
//! Se compila el crate con la feature activada y se ejercita el router sobre
//! el índice de memoria, sin levantar un socket real. Los tests de la CLI y
//! del crawler no cubren `api` precisamente porque esta feature es opcional.

#![cfg(feature = "api")]

use std::path::PathBuf;

use axum::body::Body;
use axum::http::{Request, StatusCode};
use motor_indexado::{api::router, InvertedIndex};
use tower::ServiceExt;

fn indice_de_prueba() -> InvertedIndex {
    let mut indice = InvertedIndex::new();
    indice.add_document(PathBuf::from("a.txt"), "hola mundo");
    indice.add_document(PathBuf::from("b.txt"), "hola rust");
    indice
}

#[tokio::test]
async fn el_endpoint_de_busqueda_devuelve_resultados() {
    let app = router(indice_de_prueba());

    let respuesta = app
        .oneshot(
            Request::builder()
                .uri("/search?q=rust")
                .body(Body::empty())
                .expect("petición válida"),
        )
        .await
        .expect("el router responde");

    assert_eq!(respuesta.status(), StatusCode::OK);
    let cuerpo = axum::body::to_bytes(respuesta.into_body(), usize::MAX)
        .await
        .expect("cuerpo legible");
    let texto = String::from_utf8(cuerpo.to_vec()).expect("respuesta utf8");
    assert!(texto.contains("b.txt"));
    assert!(texto.contains("\"score\":1"));
}

#[tokio::test]
async fn la_busqueda_aplica_el_limite_por_defecto() {
    let mut indice = InvertedIndex::new();
    for i in 0..30 {
        indice.add_document(PathBuf::from(format!("doc{i}.txt")), "hola mundo");
    }
    let app = router(indice);

    let respuesta = app
        .oneshot(
            Request::builder()
                .uri("/search?q=hola")
                .body(Body::empty())
                .expect("petición válida"),
        )
        .await
        .expect("el router responde");

    assert_eq!(respuesta.status(), StatusCode::OK);
    let cuerpo = axum::body::to_bytes(respuesta.into_body(), usize::MAX)
        .await
        .expect("cuerpo legible");
    let texto = String::from_utf8(cuerpo.to_vec()).expect("respuesta utf8");
    // El límite por defecto es 20: de 30 documentos, se devuelven 20.
    assert!(texto.contains("\"results\":["));
    assert_eq!(texto.matches("\"path\":").count(), 20);
}

#[tokio::test]
async fn la_busqueda_respeta_el_limite_pedido() {
    let app = router(indice_de_prueba());

    let respuesta = app
        .oneshot(
            Request::builder()
                .uri("/search?q=hola&limit=1")
                .body(Body::empty())
                .expect("petición válida"),
        )
        .await
        .expect("el router responde");

    assert_eq!(respuesta.status(), StatusCode::OK);
    let cuerpo = axum::body::to_bytes(respuesta.into_body(), usize::MAX)
        .await
        .expect("cuerpo legible");
    let texto = String::from_utf8(cuerpo.to_vec()).expect("respuesta utf8");
    assert_eq!(texto.matches("\"path\":").count(), 1);
}

#[tokio::test]
async fn la_busqueda_sin_coincidencias_devuelve_lista_vacia() {
    let app = router(indice_de_prueba());

    let respuesta = app
        .oneshot(
            Request::builder()
                .uri("/search?q=inexistente")
                .body(Body::empty())
                .expect("petición válida"),
        )
        .await
        .expect("el router responde");

    assert_eq!(respuesta.status(), StatusCode::OK);
    let cuerpo = axum::body::to_bytes(respuesta.into_body(), usize::MAX)
        .await
        .expect("cuerpo legible");
    let texto = String::from_utf8(cuerpo.to_vec()).expect("respuesta utf8");
    assert!(texto.contains("\"results\":[]"));
}

#[tokio::test]
async fn la_busqueda_sin_query_devuelve_un_error_de_peticion() {
    let app = router(indice_de_prueba());

    let respuesta = app
        .oneshot(
            Request::builder()
                .uri("/search")
                .body(Body::empty())
                .expect("petición válida"),
        )
        .await
        .expect("el router responde");

    assert_eq!(respuesta.status(), StatusCode::BAD_REQUEST);
}