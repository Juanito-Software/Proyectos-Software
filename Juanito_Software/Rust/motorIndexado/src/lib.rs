//! Motor de indexación y búsqueda local — mini Google.
//!
//! Índice invertido, crawler de disco, búsqueda rápida y CLI.

pub mod index;
pub mod tokenizer;
pub mod crawler;
pub mod search;

#[cfg(feature = "api")]
pub mod api;

pub use index::InvertedIndex;
pub use tokenizer::tokenize;
pub use crawler::index_directory;
pub use search::SearchResult;
pub use search::search;
