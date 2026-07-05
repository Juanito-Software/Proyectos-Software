//! Tokenización de texto para el índice invertido.
//! Normaliza a minúsculas y divide por caracteres no alfanuméricos.

/// Tokeniza un texto: minúsculas y tokens alfanuméricos.
/// Ignora tokens de longitud &lt; 2 para reducir ruido.
pub fn tokenize(text: &str) -> Vec<String> {
    text.to_lowercase()
        .split(|c: char| !c.is_alphanumeric())
        .filter(|s| s.len() >= 2)
        .map(|s| s.to_string())
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tokenize_basic() {
        let t = tokenize("Hello, world! Rust 2021.");
        assert!(t.contains(&"hello".to_string()));
        assert!(t.contains(&"world".to_string()));
        assert!(t.contains(&"rust".to_string()));
    }

    #[test]
    fn tokenize_ignores_short() {
        let t = tokenize("I a be");
        assert!(!t.contains(&"i".to_string()));
        assert!(!t.contains(&"a".to_string()));
        assert!(t.contains(&"be".to_string()));
    }
}
