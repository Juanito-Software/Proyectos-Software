//! CLI del motor de indexación y búsqueda local.

use std::path::PathBuf;

use anyhow::Result;
use clap::{Parser, Subcommand};

use motor_indexado::{index_directory, search, InvertedIndex, SearchResult};

#[derive(Parser)]
#[command(name = "motor-indexado")]
#[command(about = "Motor de indexación y búsqueda local — mini Google", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Indexa un directorio y guarda el índice en un archivo JSON.
    Index {
        /// Ruta del directorio a indexar
        #[arg(value_name = "DIR")]
        dir: PathBuf,

        /// Archivo donde guardar el índice (por defecto: índice.json en el directorio actual)
        #[arg(short, long, value_name = "FILE")]
        output: Option<PathBuf>,

        /// Profundidad máxima de carpetas (por defecto: sin límite)
        #[arg(short, long)]
        depth: Option<usize>,
    },

    /// Busca en un índice existente.
    Search {
        /// Archivo del índice (por defecto: índice.json)
        #[arg(short, long, value_name = "FILE")]
        index: Option<PathBuf>,

        /// Consulta de búsqueda
        #[arg(value_name = "QUERY")]
        query: String,

        /// Número máximo de resultados
        #[arg(short, long, default_value = "20")]
        limit: usize,
    },

    /// Indexa y busca en una sola pasada (sin guardar índice).
    Run {
        /// Ruta del directorio a indexar
        #[arg(value_name = "DIR")]
        dir: PathBuf,

        /// Consulta de búsqueda
        #[arg(value_name = "QUERY")]
        query: String,

        /// Número máximo de resultados
        #[arg(short, long, default_value = "20")]
        limit: usize,

        /// Profundidad máxima de carpetas
        #[arg(short, long)]
        depth: Option<usize>,
    },

    /// Arranca la API HTTP (requiere compilar con --features api).
    #[cfg(feature = "api")]
    Serve {
        /// Archivo del índice
        #[arg(short, long, value_name = "FILE", default_value = "indice.json")]
        index: PathBuf,

        /// Dirección y puerto (ej. 127.0.0.1:3030)
        #[arg(short, long, default_value = "127.0.0.1:3030")]
        bind: String,
    },
}

const DEFAULT_INDEX_FILE: &str = "indice.json";

fn load_index(path: &std::path::Path) -> Result<InvertedIndex> {
    let json = std::fs::read_to_string(path)?;
    let index: InvertedIndex = serde_json::from_str(&json)?;
    Ok(index)
}

fn save_index(index: &InvertedIndex, path: &std::path::Path) -> Result<()> {
    let json = serde_json::to_string_pretty(index)?;
    std::fs::write(path, json)?;
    Ok(())
}

fn print_results(results: &[SearchResult]) {
    if results.is_empty() {
        println!("No se encontraron resultados.");
        return;
    }
    for (i, r) in results.iter().enumerate() {
        println!(
            "{}. {} (score: {}, términos: {:?})",
            i + 1,
            r.path.display(),
            r.score,
            r.matches
        );
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Index { dir, output, depth } => {
            println!("Indexando {} ...", dir.display());
            let index = index_directory(&dir, depth);
            println!(
                "Documentos: {}, Términos: {}",
                index.doc_count(),
                index.term_count()
            );
            let out = output.unwrap_or_else(|| PathBuf::from(DEFAULT_INDEX_FILE));
            save_index(&index, &out)?;
            println!("Índice guardado en {}", out.display());
        }

        Commands::Search { index, query, limit } => {
            let path = index.unwrap_or_else(|| PathBuf::from(DEFAULT_INDEX_FILE));
            let idx = load_index(&path)?;
            println!("Buscando \"{}\" (índice: {}) ...", query, path.display());
            let results = search(&idx, &query, limit);
            print_results(&results);
        }

        Commands::Run { dir, query, limit, depth } => {
            println!("Indexando {} ...", dir.display());
            let index = index_directory(&dir, depth);
            println!(
                "Documentos: {}, Términos: {}",
                index.doc_count(),
                index.term_count()
            );
            println!("Buscando \"{}\" ...", query);
            let results = search(&index, &query, limit);
            print_results(&results);
        }

        #[cfg(feature = "api")]
        Commands::Serve { index, bind } => {
            let rt = tokio::runtime::Runtime::new()?;
            rt.block_on(motor_indexado::api::serve(&bind, &index))?;
        }
    }

    Ok(())
}
