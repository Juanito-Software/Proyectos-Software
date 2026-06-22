/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package db;

/**
 *
 * @author User
 */
import java.sql.*;

public class Descarga {
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";
       
    // Método para registrar una descarga
    public static void registrarDescarga(int usuarioID, int juegoID, String fechaDescarga) {
        String sql = "INSERT INTO descarga (UsuarioID, JuegoID, fechaDescarga) VALUES (?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, usuarioID);
            stmt.setInt(2, juegoID);
            stmt.setString(3, fechaDescarga);

            stmt.executeUpdate();
            System.out.println("Descarga registrada exitosamente.");
        } catch (SQLException e) {
            System.err.println("Error al registrar la descarga: " + e.getMessage());
        }
    }

    // Método para obtener descargas por usuario
    public static void obtenerDescargasPorUsuario(int usuarioID) {
        String sql = "SELECT * FROM descarga WHERE UsuarioID = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, usuarioID);
            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                System.out.println("ID: " + rs.getInt("id"));
                System.out.println("Usuario ID: " + rs.getInt("UsuarioID"));
                System.out.println("Juego ID: " + rs.getInt("JuegoID"));
                System.out.println("Fecha de Descarga: " + rs.getString("fechaDescarga"));
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener descargas del usuario: " + e.getMessage());
        }
    }

    // Método para eliminar una descarga por su ID
    public static void eliminarDescarga(int id) {
        String sql = "DELETE FROM descarga WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);

            int rowsDeleted = stmt.executeUpdate();
            if (rowsDeleted > 0) {
                System.out.println("Descarga eliminada exitosamente.");
            } else {
                System.out.println("Descarga no encontrada.");
            }
        } catch (SQLException e) {
            System.err.println("Error al eliminar la descarga: " + e.getMessage());
        }
    }
    
    // Método para eliminar una descarga por su ID
    public static void eliminarDescargas () {
        String sql = "DELETE FROM descarga;";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            int rowsDeleted = stmt.executeUpdate();
            if (rowsDeleted > 0) {
                System.out.println("Descargas eliminadas exitosamente.");
            } else {
                System.out.println("Descargas no encontradas.");
            }
        } catch (SQLException e) {
            System.err.println("Error al eliminar la descarga: " + e.getMessage());
        }
    }
}
