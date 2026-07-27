/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 */

package com.mycompany.jasperreportexecutor;

/**
 *
 * @author User
 */

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import net.sf.jasperreports.engine.JRException;

import net.sf.jasperreports.engine.export.*;
import net.sf.jasperreports.view.JasperViewer;

import net.sf.jasperreports.engine.JasperExportManager;
import net.sf.jasperreports.engine.JasperFillManager;
import net.sf.jasperreports.engine.JasperPrint;

import net.sf.jasperreports.engine.export.JRXlsExporter;
import net.sf.jasperreports.engine.export.JRCsvExporter;
import net.sf.jasperreports.export.SimpleExporterInput;
import net.sf.jasperreports.export.SimpleOutputStreamExporterOutput;

public class JasperReportExecutor {

    public static void main(String[] args) throws JRException {
        Connection conn = null;

        try {
            // Configurar la conexión a la base de datos.
            // Las credenciales se leen del entorno para no versionarlas.
            // Ejecutar con:  DB_PASSWORD=... java -jar JasperReportExecutor.jar
            String dbUrl = System.getenv().getOrDefault("DB_URL", "jdbc:postgresql://localhost:5432/game");
            String dbUser = System.getenv().getOrDefault("DB_USER", "admin");
            String dbPassword = System.getenv("DB_PASSWORD");
            if (dbPassword == null || dbPassword.isBlank()) {
                throw new IllegalStateException(
                        "Falta la variable de entorno DB_PASSWORD con la contraseña de PostgreSQL.");
            }
           
            
            // Intentar obtener la conexión a la base de datos
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPassword);

            // Verificar si la conexión fue exitosa
            if (conn != null && conn.isValid(5)) {
                System.out.println("Conexión a la base de datos establecida correctamente.");

                
                
                
                // Ruta al archivo .jasper (compilado desde Jaspersoft Studio)
                String reportPath = JasperReportExecutor.class.getClassLoader().getResource("informePuntuaciones.jasper").getPath();
                //String absoluteReportPath = "C:\\Users\\User\\Desktop\\webapp_puntuaciones\\informes\\informe.jasper";

                // Parámetros del informe (si fuesen necesarios)
                //Map<String, Object> parameters = new HashMap<>();
                //parameters.put("param1", "valor1"); // Ejemplo de un parámetro
                
                // Llenar el informe con datos
                JasperPrint jasperPrint = JasperFillManager.fillReport(reportPath, null, conn); // Aquí añadirías los parámetros si los hubieras

                // Obtener la ruta base del directorio del proyecto (suponiendo que sea el directorio raíz del proyecto)
                String basePath = System.getProperty("user.dir"); // Devuelve el directorio de trabajo actual

                
                
                
                // Construir la ruta relativa a 'webapp_puntuaciones\\informes\\informe.pdf'
                Path outputPath = Paths.get(basePath, "..", "informePuntuaciones.pdf");

                // Convertir la ruta a una cadena para poder usarla
                String pdfOutputPath = outputPath.toString();

                // Exportar el informe a PDF
                JasperExportManager.exportReportToPdfFile(jasperPrint, pdfOutputPath);
                System.out.println("Informe generado en: " + pdfOutputPath);

                
                
                
                /*
                // Construir la ruta relativa a 'webapp_puntuaciones\\informes\\informe.xlsx'
                Path outputPath2 = Paths.get(basePath, "..", "informe.xlsx");
                
                // Convertir la ruta a una cadena para poder mostrarla
                String xlsxOutputPath = outputPath2.toString();
                
                // Convertir la ruta en un archivo para poder usarlo
                File outputFile2 = outputPath2.toFile();
                
                // configurar el JRXlsExporter
                JRXlsExporter exporter = new JRXlsExporter();
                //exporter.setExporterInput(new SimpleExporterInput(jasperPrint)); // Ingresamos el JasperPrint generado
                //exporter.setExporterOutput(new SimpleOutputStreamExporterOutput(outputFile2)); // Especificamos el archivo de salida
                exporter.setParameter(JRXlsExporterParameter.JASPER_PRINT, jasperPrint);
                exporter.setParameter(JRXlsExporterParameter.OUTPUT_FILE_NAME, xlsxOutputPath);
                // Exportar el informe a Excel (XLS)
                exporter.exportReport();
                System.out.println("Informe generado en: " + xlsxOutputPath);

                */
                
                /*
                // Construir la ruta relativa a 'webapp_puntuaciones\\informes\\informe.csv'
                Path outputPath3 = Paths.get(basePath, "..", "informe.csv");
                
                // Convertir la ruta a una cadena para poder mostrarla
                String csvOutputPath = outputPath3.toString();
                
                // Convertir la ruta en un ardchivo para poder usarlo
                File outputFile3 = outputPath3.toFile();
                
                JRCsvExporter exporter2 = new JRCsvExporter();
                exporter.setExporterInput(new SimpleExporterInput(jasperPrint));
                exporter.setExporterOutput(new SimpleOutputStreamExporterOutput(outputFile3));
                // Exportar el informe a CSV
                exporter.exportReport();
                System.out.println("Informe generado en: " + csvOutputPath);
                */
                
                
                
                
                
                // Ruta al archivo .jasper (compilado desde Jaspersoft Studio)
                String reportPath2 = JasperReportExecutor.class.getClassLoader().getResource("informeJugadores.jasper").getPath();
                
                // Llenar el informe con datos
                JasperPrint jasperPrint2 = JasperFillManager.fillReport(reportPath2, null, conn); // Aquí añadirías los parámetros si los hubieras
                
                
                
                
                // Construir la ruta relativa a 'webapp_puntuaciones\\informes\\informe.pdf'
                Path outputPath2 = Paths.get(basePath, "..", "informeJugadores.pdf");

                // Convertir la ruta a una cadena para poder usarla
                String pdfOutputPath2 = outputPath2.toString();

                // Exportar el informe a PDF
                JasperExportManager.exportReportToPdfFile(jasperPrint2, pdfOutputPath2);
                System.out.println("Informe generado en: " + pdfOutputPath2);
                
            } else {
                System.out.println("Conexion fallida.");
            }

        } catch (SQLException a) {
            System.out.println("Error al conectar a la base de datos");
            a.printStackTrace();
        } finally {
            try {
                // Cerrar la conexión a la base de datos si se abrió
                if (conn != null && !conn.isClosed()) {
                    conn.close();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}