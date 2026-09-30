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

    #[test]
    fn tokenize_texto_vacio_da_vacio() {
        assert!(tokenize("").is_empty());
    }

    #[test]
    fn tokenize_separa_con_guion_bajo() {
        let t = tokenize("hola_mundo");
        assert_eq!(t, vec!["hola".to_string(), "mundo".to_string()]);
    }

    #[test]
    fn tokenize_conserva_numeros() {
        let t = tokenize("Rust 2021");
        assert!(t.contains(&"2021".to_string()));
    }

    #[test]
    fn tokenize_conserva_solo_alfanumericos() {
        let t = tokenize("café — ¡muy bueno!");
        assert!(t.contains(&"café".to_string()));
        assert!(t.contains(&"muy".to_string()));
        assert!(t.contains(&"bueno".to_string()));
    }
}
