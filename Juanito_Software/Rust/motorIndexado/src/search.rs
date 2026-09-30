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

#[cfg(test)]
mod tests {
    use super::*;

    fn indice_de_prueba() -> InvertedIndex {
        let mut indice = InvertedIndex::new();
        indice.add_document(PathBuf::from("a.txt"), "hola mundo");
        indice.add_document(PathBuf::from("b.txt"), "hola rust otro");
        indice
    }

    #[test]
    fn consulta_vacia_devuelve_sin_resultados() {
        let indice = indice_de_prueba();
        assert!(search(&indice, "", 10).is_empty());
        assert!(search(&indice, "   ", 10).is_empty());
    }

    #[test]
    fn consulta_sin_coincidencias_devuelve_sin_resultados() {
        let indice = indice_de_prueba();
        assert!(search(&indice, "python", 10).is_empty());
    }

    #[test]
    fn consulta_de_un_termino_devuelve_documentos_con_score() {
        let indice = indice_de_prueba();
        let resultados = search(&indice, "rust", 10);
        assert_eq!(resultados.len(), 1);
        assert_eq!(resultados[0].path, PathBuf::from("b.txt"));
        assert_eq!(resultados[0].score, 1);
        assert_eq!(resultados[0].matches, vec!["rust".to_string()]);
    }

    #[test]
    fn varios_terminos_acumulan_score_por_documento() {
        let indice = indice_de_prueba();
        let resultados = search(&indice, "hola mundo", 10);
        assert_eq!(resultados.len(), 2);
        // a.txt: hola + mundo (2); b.txt: solo hola (1)
        assert_eq!(resultados[0].path, PathBuf::from("a.txt"));
        assert_eq!(resultados[0].score, 2);
        assert_eq!(resultados[0].matches.len(), 2);
    }

    #[test]
    fn resultados_ordenados_por_score_descendente() {
        let mut indice = InvertedIndex::new();
        indice.add_document(PathBuf::from("a.txt"), "hola");
        // "hola" aparece tres veces: la suma debe mandar a este documento el primero
        indice.add_document(PathBuf::from("b.txt"), "hola hola hola");

        let resultados = search(&indice, "hola", 10);

        let scores: Vec<u32> = resultados.iter().map(|r| r.score).collect();
        assert_eq!(scores, vec![3, 1]);
        assert_eq!(resultados[0].path, PathBuf::from("b.txt"));
        assert_eq!(resultados[1].path, PathBuf::from("a.txt"));
    }

    #[test]
    fn el_limite_recorta_resultados() {
        let indice = indice_de_prueba();
        let resultados = search(&indice, "hola", 1);
        assert_eq!(resultados.len(), 1);
    }
}
