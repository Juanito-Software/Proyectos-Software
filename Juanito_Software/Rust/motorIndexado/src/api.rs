//! API HTTP ligera para búsquedas (feature `api`).

use std::path::Path;
use std::sync::Arc;

use axum::{
    extract::{Query, State},
    response::Json,
    routing::get,
    Router,
};
use serde::{Deserialize, Serialize};

use crate::search::{search, SearchResult};
use crate::InvertedIndex;

#[derive(Clone)]
pub struct AppState {
    pub index: Arc<InvertedIndex>,
}

#[derive(Debug, Deserialize)]
pub struct SearchQuery {
    pub q: String,
    #[serde(default = "default_limit")]
    pub limit: usize,
}

fn default_limit() -> usize {
    20
}

#[derive(Serialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResultDto>,
}

#[derive(Serialize)]
pub struct SearchResultDto {
    pub path: String,
    pub score: u32,
    pub matches: Vec<String>,
}

impl From<SearchResult> for SearchResultDto {
    fn from(r: SearchResult) -> Self {
        Self {
            path: r.path.to_string_lossy().into_owned(),
            score: r.score,
            matches: r.matches,
        }
    }
}

async fn search_handler(
    State(state): State<AppState>,
    Query(params): Query<SearchQuery>,
) -> Json<SearchResponse> {
    let results = search(state.index.as_ref(), &params.q, params.limit);
    let results = results.into_iter().map(SearchResultDto::from).collect();
    Json(SearchResponse { results })
}

/// Crea el router de la API (índice cargado en memoria).
pub fn router(index: InvertedIndex) -> Router {
    let state = AppState {
        index: Arc::new(index),
    };
    Router::new()
        .route("/search", get(search_handler))
        .with_state(state)
}

/// Arranca el servidor en `addr` (ej. `127.0.0.1:3030`) con el índice en `index_path`.
pub async fn serve(addr: &str, index_path: &Path) -> anyhow::Result<()> {
    let json = std::fs::read_to_string(index_path)?;
    let index: InvertedIndex = serde_json::from_str(&json)?;
    let app = router(index);
    let listener = tokio::net::TcpListener::bind(addr).await?;
    println!("API escuchando en http://{}", addr);
    println!("  GET /search?q=consulta&limit=20");
    axum::serve(listener, app).await?;
    Ok(())
}
