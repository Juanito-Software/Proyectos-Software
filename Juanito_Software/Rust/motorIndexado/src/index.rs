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
