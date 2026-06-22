/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package db;

/**
 *
 * @author User
 */
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.sql.*;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

public class Game {
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";

    // Método para agregar un juego
    public static void addGame(String name, String departure_date, String category, String continent, String description, String price, String units, String platform, String peggy, String usuario, Blob GameImage) throws FileNotFoundException, IOException {
        String sql = "INSERT INTO games (name, departure_date, category, continent, description, price, units, platform, peggy, usuario, logo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            stmt.setString(2, departure_date);
            stmt.setString(3, category);
            stmt.setString(4, continent);
            stmt.setString(5, description);
            stmt.setString(6, price);
            stmt.setString(7, units);
            stmt.setString(8, platform);
            stmt.setString(9, peggy);
            stmt.setString(10, usuario);
   
            // Obtener InputStream del Blob
            InputStream blobInputStream = GameImage.getBinaryStream();
            stmt.setBinaryStream(11, blobInputStream);
            
            stmt.executeUpdate();
            System.out.println("Juego agregado exitosamente.");
        } catch (SQLException e) {
            System.err.println("Error al agregar juego: " + e.getMessage());
        }
    }

    
    // Método para leer un juego por su ID
    public static void getGameById(int id) {
        String sql = "SELECT * FROM games WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                System.out.println("ID: " + rs.getInt("id"));
                System.out.println("Nombre: " + rs.getString("name"));
                System.out.println("Fecha de salida: " + rs.getString("departure_date"));
                System.out.println("Categoría: " + rs.getString("category"));
                System.out.println("Continente: " + rs.getString("continent"));
                System.out.println("Descripción: " + rs.getString("description"));
                System.out.println("Precio: " + rs.getString("price"));
                System.out.println("Unidades: " + rs.getString("units"));
                System.out.println("Plataforma: " + rs.getString("platform"));
                System.out.println("PEGI: " + rs.getString("peggy"));
                System.out.println("Usuario: " + rs.getString("usuario"));
            } else {
                System.out.println("Juego no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al leer juego: " + e.getMessage());
        }
    }

    // Método para actualizar un juego por su ID
    public static void updateGame(int id, String name, String departure_date, String category, String continent, String description, String price, String units, String platform, String peggy, String usuario) {
        String sql = "UPDATE games SET name = ?, departure_date = ?, category = ?, continent = ?, description = ?, price = ?, units = ?, platform = ?, peggy = ?, usuario = ? WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            stmt.setString(2, departure_date);
            stmt.setString(3, category);
            stmt.setString(4, continent);
            stmt.setString(5, description);
            stmt.setString(6, price);
            stmt.setString(7, units);
            stmt.setString(8, platform);
            stmt.setString(9, peggy);
            stmt.setString(10, usuario);
            stmt.setInt(11, id);

            int rowsUpdated = stmt.executeUpdate();
            if (rowsUpdated > 0) {
                System.out.println("Juego actualizado exitosamente.");
            } else {
                System.out.println("Juego no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al actualizar juego: " + e.getMessage());
        }
    }

    // Método para eliminar un juego por su ID
    public static void deleteGame(int id) {
        String sql = "DELETE FROM games WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);

            int rowsDeleted = stmt.executeUpdate();
            if (rowsDeleted > 0) {
                System.out.println("Juego eliminado exitosamente.");
            } else {
                System.out.println("Juego no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al eliminar juego: " + e.getMessage());
        }
    }

    // Método para obtener el ID de un juego por nombre y descripción
    public static int getGameIdByNameAndDescription(String name, String description) {
        String sql = "SELECT id FROM games WHERE name = ? AND description = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            stmt.setString(2, description);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                return rs.getInt("id");
            } else {
                System.out.println("Juego no encontrado.");
                return -1; // Retornar -1 si no se encuentra el juego
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el ID del juego: " + e.getMessage());
            return -1; // Retornar -1 en caso de error
        }
    }
    
    // Método para obtener el ID de un juego por nombre y descripción
    public static int getGameIdByName(String name) {
        String sql = "SELECT id FROM games WHERE name = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, name);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                return rs.getInt("id");
            } else {
                System.out.println("Juego no encontrado.");
                return -1; // Retornar -1 si no se encuentra el juego
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el ID del juego: " + e.getMessage());
            return -1; // Retornar -1 en caso de error
        }
    }
    
    public static Blob getGameLogoByName(String gameName) {
        Blob logoBlob = null;
        String sql = "SELECT logo FROM games WHERE name = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            // Configurar el parámetro de la consulta
            stmt.setString(1, gameName);

            try (ResultSet rs = stmt.executeQuery()) {
                // Procesar el resultado de la consulta
                if (rs.next()) {
                    logoBlob = rs.getBlob("logo");
                } else {
                    System.out.println("Logo no encontrado para el juego: " + gameName);
                }
            }

        } catch (SQLException e) {
            System.err.println("Error al obtener el logo del juego: " + e.getMessage());
        }

        return logoBlob;
    }
}
