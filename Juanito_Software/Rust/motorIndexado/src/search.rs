//! Búsqueda sobre el índice invertido.
//! Soporta consultas de varias palabras y ranking por relevancia (TF).

use std::collections::HashMap;
use std::path::PathBuf;

use crate::index::InvertedIndex;
use crate::tokenizer;

/// Un resultado de búsqueda: ruta del archivo y puntuación (número de coincidencias).
#[derive(Clone, Debug)]
pub struct SearchResult {
    pub path: PathBuf,
    pub score: u32,
    pub matches: Vec<String>,
}

/// Busca en el índice por la query (varias palabras).
/// Devuelve resultados ordenados por score descendente.
pub fn search(index: &InvertedIndex, query: &str, limit: usize) -> Vec<SearchResult> {
    let terms: Vec<String> = tokenizer::tokenize(query);
    if terms.is_empty() {
        return vec![];
    }

    // Por cada documento, sumar las frecuencias de los términos que coinciden
    let mut doc_scores: HashMap<PathBuf, (u32, Vec<String>)> = HashMap::new();

    for term in &terms {
        if let Some(postings) = index.postings(term) {
            for (path, count) in postings {
                doc_scores
                    .entry(path.clone())
                    .and_modify(|(score, matches)| {
                        *score += count;
                        if !matches.contains(term) {
                            matches.push(term.clone());
                        }
                    })
                    .or_insert_with(|| (*count, vec![term.clone()]));
            }
        }
    }

    let mut results: Vec<SearchResult> = doc_scores
        .into_iter()
        .map(|(path, (score, matches))| SearchResult { path, score, matches })
        .collect();
    results.sort_by(|a, b| b.score.cmp(&a.score));
    results.truncate(limit);
    results
}
