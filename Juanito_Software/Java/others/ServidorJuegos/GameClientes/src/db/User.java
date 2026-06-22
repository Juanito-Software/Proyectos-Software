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

public class User {
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";

    // Método para agregar un usuario
    public static void addUser(String nombre, String apellido, String username, String dni, String phoneNumber, String email, String password, String role) {
        String sql = "INSERT INTO users (nombre, apellido, username, dni, phoneNumber, email, password, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, nombre);
            stmt.setString(2, apellido);
            stmt.setString(3, username);
            stmt.setString(4, dni);
            stmt.setString(5, phoneNumber);
            stmt.setString(6, email);
            stmt.setString(7, password);
            stmt.setString(8, role);

            stmt.executeUpdate();
            System.out.println("Usuario agregado exitosamente.");
        } catch (SQLException e) {
            System.err.println("Error al agregar usuario: " + e.getMessage());
        }
    }

    // Método para leer un usuario por su ID
    public static void getUserById(int id) {
        String sql = "SELECT * FROM users WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                System.out.println("ID: " + rs.getInt("id"));
                System.out.println("Nombre: " + rs.getString("nombre"));
                System.out.println("Apellido: " + rs.getString("apellido"));
                System.out.println("Username: " + rs.getString("username"));
                System.out.println("DNI: " + rs.getString("dni"));
                System.out.println("Teléfono: " + rs.getString("phoneNumber"));
                System.out.println("Email: " + rs.getString("email"));
                System.out.println("Rol: " + rs.getString("role"));
            } else {
                System.out.println("Usuario no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al leer usuario: " + e.getMessage());
        }
    }

    // Método para actualizar un usuario por su ID
    public static void updateUser(int id, String nombre, String apellido, String username, String dni, String phoneNumber, String email, String password, String role) {
        String sql = "UPDATE users SET nombre = ?, apellido = ?, username = ?, dni = ?, phoneNumber = ?, email = ?, password = ?, role = ? WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, nombre);
            stmt.setString(2, apellido);
            stmt.setString(3, username);
            stmt.setString(4, dni);
            stmt.setString(5, phoneNumber);
            stmt.setString(6, email);
            stmt.setString(7, password);
            stmt.setString(8, role);
            stmt.setInt(9, id);

            int rowsUpdated = stmt.executeUpdate();
            if (rowsUpdated > 0) {
                System.out.println("Usuario actualizado exitosamente.");
            } else {
                System.out.println("Usuario no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al actualizar usuario: " + e.getMessage());
        }
    }

    // Método para eliminar un usuario por su ID
    public static void deleteUser(int id) {
        String sql = "DELETE FROM users WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);

            int rowsDeleted = stmt.executeUpdate();
            if (rowsDeleted > 0) {
                System.out.println("Usuario eliminado exitosamente.");
            } else {
                System.out.println("Usuario no encontrado.");
            }
        } catch (SQLException e) {
            System.err.println("Error al eliminar usuario: " + e.getMessage());
        }
    }

    // Método para obtener el ID de un usuario por nombre y apellido
    public static int getUserIdByNameAndSurname(String nombre, String apellido) {
        String sql = "SELECT id FROM users WHERE nombre = ? AND apellido = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, nombre);
            stmt.setString(2, apellido);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                return rs.getInt("id");
            } else {
                System.out.println("Usuario no encontrado.");
                return -1; // Retornar -1 si no se encuentra el usuario
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el ID del usuario: " + e.getMessage());
            return -1; // Retornar -1 en caso de error
        }
    }
    
    // Método para obtener el ID de un usuario por nombre y apellido
    public static int getUserIdByUsername(String username) {
        String sql = "SELECT id FROM users WHERE username = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, username);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                return rs.getInt("id");
            } else {
                System.out.println("Usuario no encontrado.");
                return -1; // Retornar -1 si no se encuentra el usuario
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el ID del usuario: " + e.getMessage());
            return -1; // Retornar -1 en caso de error
        }
    }

    // Método para obtener el rol de un usuario por username
    public static String getUserRoleByUsername(String username) {
        String sql = "SELECT role FROM users WHERE username = ?";
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, username);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                return rs.getString("role");
            } else {
                System.out.println("Usuario no encontrado.");
                return null; // Retornar null si no se encuentra el usuario
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el rol del usuario: " + e.getMessage());
            return null; // Retornar null en caso de error
        }
    }   
}
