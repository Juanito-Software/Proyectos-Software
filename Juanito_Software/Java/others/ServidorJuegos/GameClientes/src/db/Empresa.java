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
import java.io.IOException;
import java.io.InputStream;
import java.sql.*;
import javax.imageio.ImageIO;
import javax.swing.ImageIcon;

public class Empresa {
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";

    // Método para registrar una empresa
    public static void registrarEmpresa(String nombre, String descripcion, String fechaCreacion, Blob logo) {
        String sql = "INSERT INTO empresas (nombre, descripcion, fechaCreacion, logo) VALUES (?, ?, ?, ?)";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, nombre);
            stmt.setString(2, descripcion);
            stmt.setString(3, fechaCreacion);
            
            // Obtener InputStream del Blob
            InputStream blobInputStream = logo.getBinaryStream();
            stmt.setBinaryStream(4, blobInputStream);


            stmt.executeUpdate();
            System.out.println("Empresa registrada exitosamente.");
        } catch (SQLException e) {
            System.err.println("Error al registrar la empresa: " + e.getMessage());
        }
    }

    // Método para obtener una empresa por su ID
    public static void obtenerEmpresa(int id) {
        String sql = "SELECT * FROM empresas WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                System.out.println("ID: " + rs.getInt("id"));
                System.out.println("Nombre: " + rs.getString("nombre"));
                System.out.println("Descripción: " + rs.getString("descripcion"));
                System.out.println("Fecha de Creación: " + rs.getString("fechaCreacion"));
                System.out.println("Ruta al logo: " + rs.getString("logo"));
            } else {
                System.out.println("Empresa no encontrada.");
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener la empresa: " + e.getMessage());
        }
    }

    // Método para actualizar una empresa por su ID
    public static void actualizarEmpresa(int id, String nombre, String descripcion, String fechaCreacion, Blob logo) {
        String sql = "UPDATE empresas SET nombre = ?, descripcion = ?, fechaCreacion = ?, logo = ?, WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, nombre);
            stmt.setString(2, descripcion);
            stmt.setString(3, fechaCreacion);
            // Obtener InputStream del Blob
            InputStream blobInputStream = logo.getBinaryStream();
            stmt.setBinaryStream(4, blobInputStream);
            stmt.setInt(5, id);

            int rowsUpdated = stmt.executeUpdate();
            if (rowsUpdated > 0) {
                System.out.println("Empresa actualizada exitosamente.");
            } else {
                System.out.println("Empresa no encontrada.");
            }
        } catch (SQLException e) {
            System.err.println("Error al actualizar la empresa: " + e.getMessage());
        }
    }

    // Método para eliminar una empresa por su ID
    public static void eliminarEmpresa(int id) {
        String sql = "DELETE FROM empresas WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, id);

            int rowsDeleted = stmt.executeUpdate();
            if (rowsDeleted > 0) {
                System.out.println("Empresa eliminada exitosamente.");
            } else {
                System.out.println("Empresa no encontrada.");
            }
        } catch (SQLException e) {
            System.err.println("Error al eliminar la empresa: " + e.getMessage());
        }
    }
    
    // Método para obtener la URL del logo por ID de la empresa
    public static String getImageUrlByCompanyId(int companyId) {
        String imageUrl = null;
        String sql = "SELECT logo FROM empresas WHERE id = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setInt(1, companyId);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                imageUrl = rs.getString("logo");
            } else {
                System.err.println("Empresa no encontrada con ID: " + companyId);
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener la URL del logo: " + e.getMessage());
        }

        return imageUrl;
    }
    
    // Método para obtener el ID de la empresa por su nombre
    public static int getCompanyIdByName(String companyName) {
        int companyId = -1; // Valor predeterminado si no se encuentra la empresa
        String sql = "SELECT id FROM empresas WHERE nombre = ?";

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
            PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, companyName);
            ResultSet rs = stmt.executeQuery();

            if (rs.next()) {
                companyId = rs.getInt("id");
            } else {
                System.err.println("Empresa no encontrada con el nombre: " + companyName);
            }
        } catch (SQLException e) {
            System.err.println("Error al obtener el ID de la empresa: " + e.getMessage());
        }

        return companyId;
    }
    
    public static ImageIcon getEmpresaLogoByName(String empresaName) throws IOException {
        String sql = "SELECT logo FROM empresas WHERE nombre = ?";  // Suponiendo que la columna que contiene el logo se llama 'logo'

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            // Asignar el ID de la empresa al parámetro de la consulta
            stmt.setString(1, empresaName);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    Blob logoBlob = rs.getBlob("logo");  // Asegúrate de que 'logo' es el nombre correcto de la columna en la base de datos
                    if (logoBlob != null) {
                        InputStream inputStream = logoBlob.getBinaryStream();
                        BufferedImage bufferedImage = ImageIO.read(inputStream);

                        if (bufferedImage != null) {
                            return new ImageIcon(bufferedImage);
                        }else {
                            System.err.println("No se pudo leer la imagen del logo para la empresa: " + empresaName);
                        }
                    }else{
                        System.err.println("No se encontró el logo para la empresa: " + empresaName);
                    }
                }
            }
        } catch (SQLException | IOException e) {
            System.err.println("Error al recuperar el logo de la empresa desde la base de datos: " + e.getMessage());
            e.printStackTrace();
        }
        return null;  // Si algo falla o no se encuentra el logo, devuelve null
    }
}

