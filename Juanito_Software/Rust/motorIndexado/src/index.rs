//! Índice invertido: término -> lista de (ruta_archivo, posiciones).
//! Permite búsquedas ultrarrápidas por palabra.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

use crate::tokenizer;

/// Para cada término, guardamos en qué archivos aparece y en qué posiciones (opcional).
#[derive(Clone, Debug, Default)]
pub struct InvertedIndex {
    /// término -> (ruta_archivo -> conteo de ocurrencias)
    term_to_docs: HashMap<String, HashMap<PathBuf, u32>>,
    /// Número total de documentos indexados
    doc_count: usize,
}

/// Versión serializable del índice (PathBuf como String en JSON).
#[derive(Serialize, Deserialize)]
struct InvertedIndexSerde {
    term_to_docs: HashMap<String, HashMap<String, u32>>,
    doc_count: usize,
}

impl InvertedIndex {
    fn to_serializable(&self) -> InvertedIndexSerde {
        let term_to_docs = self
            .term_to_docs
            .iter()
            .map(|(k, v)| {
                (
                    k.clone(),
                    v.iter().map(|(p, c)| (p.to_string_lossy().into_owned(), *c)).collect(),
                )
            })
            .collect();
        InvertedIndexSerde {
            term_to_docs,
            doc_count: self.doc_count,
        }
    }

    fn from_serializable(s: InvertedIndexSerde) -> Self {
        let term_to_docs = s
            .term_to_docs
            .into_iter()
            .map(|(k, v)| {
                (
                    k,
                    v.into_iter().map(|(p, c)| (PathBuf::from(p), c)).collect(),
                )
            })
            .collect();
        Self {
            term_to_docs,
            doc_count: s.doc_count,
        }
    }
}

impl serde::Serialize for InvertedIndex {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        self.to_serializable().serialize(serializer)
    }
}

impl<'de> serde::Deserialize<'de> for InvertedIndex {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        InvertedIndexSerde::deserialize(deserializer).map(Self::from_serializable)
    }
}

impl InvertedIndex {
    pub fn new() -> Self {
        Self {
            term_to_docs: HashMap::new(),
            doc_count: 0,
        }
    }

    /// Añade un documento al índice: tokeniza su contenido y actualiza el índice invertido.
    pub fn add_document(&mut self, path: PathBuf, content: &str) {
        let tokens = tokenizer::tokenize(content);
        for token in tokens {
            self.term_to_docs
                .entry(token)
                .or_default()
                .entry(path.clone())
                .and_modify(|c| *c += 1)
                .or_insert(1);
        }
        self.doc_count += 1;
    }

    /// Devuelve los documentos que contienen un término, con su frecuencia.
    pub fn postings(&self, term: &str) -> Option<&HashMap<PathBuf, u32>> {
        let term_lower = term.to_lowercase();
        self.term_to_docs.get(&term_lower)
    }

    /// Número de documentos indexados.
    pub fn doc_count(&self) -> usize {
        self.doc_count
    }

    /// Número de términos únicos en el índice.
    pub fn term_count(&self) -> usize {
        self.term_to_docs.len()
    }

    /// Merge de otro índice (útil para indexación paralela).
    pub fn merge(&mut self, other: InvertedIndex) {
        for (term, docs) in other.term_to_docs {
            for (path, count) in docs {
                *self.term_to_docs.entry(term.clone()).or_default().entry(path).or_insert(0) += count;
            }
        }
        self.doc_count += other.doc_count;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn path(nombre: &str) -> PathBuf {
        PathBuf::from(format!("doc/{nombre}"))
    }

    #[test]
    fn nuevo_indice_empieza_vacio() {
        let indice = InvertedIndex::new();
        assert_eq!(indice.doc_count(), 0);
        assert_eq!(indice.term_count(), 0);
    }

    #[test]
    fn add_document_indexa_terminos_y_cuenta_documentos() {
        let mut indice = InvertedIndex::new();
        indice.add_document(path("a.txt"), "hola mundo hola");
        assert_eq!(indice.doc_count(), 1);
        assert_eq!(indice.term_count(), 2);

        let postings = indice.postings("hola").expect("término presente");
        assert_eq!(postings.len(), 1);
        assert_eq!(postings.get(&path("a.txt")), Some(&2));
    }

    #[test]
    fn add_document_acumula_varios_documentos_por_termino() {
        let mut indice = InvertedIndex::new();
        indice.add_document(path("a.txt"), "hola mundo");
        indice.add_document(path("b.md"), "hola rust");
        assert_eq!(indice.doc_count(), 2);
        assert_eq!(indice.term_count(), 3);

        let postings = indice.postings("hola").expect("término presente");
        assert_eq!(postings.len(), 2);
        assert_eq!(postings.get(&path("b.md")), Some(&1));
    }

    #[test]
    fn postings_normaliza_a_minusculas() {
        let mut indice = InvertedIndex::new();
        indice.add_document(path("a.txt"), "Hola");
        assert!(indice.postings("hola").is_some());
        assert!(indice.postings("HOLA").is_some());
    }

    #[test]
    fn postings_devuelve_none_con_termino_ausente() {
        let indice = InvertedIndex::new();
        assert!(indice.postings("inexistente").is_none());
    }

    #[test]
    fn merge_suma_documentos_y_frecuencias() {
        let mut destino = InvertedIndex::new();
        destino.add_document(path("a.txt"), "hola");

        let mut origen = InvertedIndex::new();
        origen.add_document(path("a.txt"), "hola mundo");

        destino.merge(origen);

        assert_eq!(destino.doc_count(), 2);
        assert_eq!(destino.term_count(), 2);
        let postings = destino.postings("hola").expect("término presente");
        // El merge suma frecuencias por documento, no las machaca
        assert_eq!(postings.get(&path("a.txt")), Some(&2));
    }

    #[test]
    fn el_indice_hace_roundtrip_con_serde_json() {
        let mut indice = InvertedIndex::new();
        indice.add_document(path("a.txt"), "hola mundo");

        let json = serde_json::to_string(&indice).expect("serializable");
        let recuperado: InvertedIndex = serde_json::from_str(&json).expect("deserializable");

        assert_eq!(recuperado.doc_count(), 1);
        assert_eq!(recuperado.term_count(), 2);
        assert!(recuperado.postings("hola").is_some());
    }
}
