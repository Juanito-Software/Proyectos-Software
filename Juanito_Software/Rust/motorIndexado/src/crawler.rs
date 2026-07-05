//! Crawler: recorre el disco, lee archivos de texto e indexa con el índice invertido.
//! Usa Rayon para paralelizar el trabajo (concurrencia real en Rust).

use std::fs;
use std::path::{Path, PathBuf};

use rayon::prelude::*;
use walkdir::WalkDir;

use crate::index::InvertedIndex;

/// Extensiones que consideramos "texto" para indexar.
const TEXT_EXTENSIONS: &[&str] = &[
    "txt", "md", "rs", "py", "js", "ts", "json", "toml", "yml", "yaml",
    "html", "css", "xml", "csv", "log", "sql", "sh", "bat", "ps1",
];

fn is_text_extension(path: &Path) -> bool {
    path.extension()
        .and_then(|e| e.to_str())
        .map(|e| TEXT_EXTENSIONS.contains(&e.to_lowercase().as_str()))
        .unwrap_or(false)
}

/// Intenta leer el archivo como UTF-8; si falla, intenta Latin1 (encoding_rs).
fn read_file_text(path: &Path) -> Option<String> {
    let bytes = fs::read(path).ok()?;
    if let Ok(s) = String::from_utf8(bytes.clone()) {
        return Some(s);
    }
    let (decoded, _, _) = encoding_rs::WINDOWS_1252.decode(&bytes);
    Some(decoded.into_owned())
}

/// Indexa un único archivo; devuelve None si no es indexable o no se pudo leer.
fn index_file(path: PathBuf) -> Option<(PathBuf, String)> {
    if !path.is_file() || !is_text_extension(&path) {
        return None;
    }
    let content = read_file_text(&path)?;
    if content.trim().is_empty() {
        return None;
    }
    Some((path, content))
}

/// Recorre `root`, indexa todos los archivos de texto y devuelve un índice invertido.
/// Usa Rayon para procesar archivos en paralelo.
pub fn index_directory(root: &Path, max_depth: Option<usize>) -> InvertedIndex {
    let walker = WalkDir::new(root)
        .follow_links(false)
        .max_depth(max_depth.unwrap_or(usize::MAX));

    let files_with_content: Vec<_> = walker
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .map(|e| e.path().to_path_buf())
        .collect();

    // Procesar en paralelo: cada hilo construye un índice parcial
    let partial_indexes: Vec<InvertedIndex> = files_with_content
        .par_iter()
        .filter_map(|path| {
            let (path, content) = index_file(path.clone())?;
            let mut idx = InvertedIndex::new();
            idx.add_document(path, &content);
            Some(idx)
        })
        .collect();

    // Merge de todos los índices parciales en uno solo
    let mut index = InvertedIndex::new();
    for partial in partial_indexes {
        index.merge(partial);
    }
    index
}
