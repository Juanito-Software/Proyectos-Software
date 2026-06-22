/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package escribirnombresarchivos;

/**
 *
 * @author User
 */
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

public class EscribirNombresArchivos {
    public static void main(String[] args) {
        String rutaCarpeta = "ruta/carpeta"; // Ruta de la carpeta que deseas buscar
        String nombreArchivoTxt = rutaCarpeta + "\\nombreArchivos.txt"; // Ruta absoluta del archivo de salida

        try (BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(nombreArchivoTxt))) {
            Files.walkFileTree(Paths.get(rutaCarpeta), new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    // Escribir el nombre del archivo en el archivo de texto
                    bufferedWriter.write(file.getFileName().toString());
                    bufferedWriter.newLine();
                    return FileVisitResult.CONTINUE;
                }
            });
            System.out.println("Se ha creado el archivo " + nombreArchivoTxt + " con los nombres de todos los archivos.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
