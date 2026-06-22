/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package gameservers;

/**
 *
 * @author User
 */
import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.io.OutputStream;
import java.nio.file.Paths;

import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class GameServers {
    private static final int SERVER_PORT = 12345; // Puerto del servidor
    static final String GAMES_DIR = "juegos"; // Ruta relativa a la carpeta de juegos
    private static ExecutorService pool = Executors.newFixedThreadPool(10); // Manejo de conexiones simultáneas

    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(SERVER_PORT)) {
            // Configurar para reutilizar la dirección
            serverSocket.setReuseAddress(true);
            
            System.out.println("Servidor iniciado en el puerto " + SERVER_PORT);
            
            while (true) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    System.out.println("Cliente conectado: " + clientSocket.getInetAddress().getHostAddress());
                    pool.execute(new ClientHandler(clientSocket));
                } catch (IOException e) {
                    System.err.println("Error al aceptar conexión: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Error al iniciar el servidor: " + e.getMessage());
        }
    }
}

class ClientHandler implements Runnable {
    private Socket socket;

    public ClientHandler(Socket socket) {
        this.socket = socket;
        try {
            // Configurar SO_LINGER
            socket.setSoLinger(true, 10);
        } catch (SocketException e) {
            System.err.println("Error al configurar SO_LINGER: " + e.getMessage());
        }
    }

    @Override
    public void run() {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             OutputStream outStream = socket.getOutputStream()) {

            String request = in.readLine();
            if (request != null && request.startsWith("DESCARGAR")) {
                String gameName = request.substring("DESCARGAR ".length()).trim();
                Path gamePath = Paths.get(GameServers.GAMES_DIR, gameName);

                if (Files.exists(gamePath) && !Files.isDirectory(gamePath)) {
                    System.out.println("Enviando archivo: " + gameName);
                    
                    try (InputStream fileIn = Files.newInputStream(gamePath);
                         BufferedOutputStream bufferedOut = new BufferedOutputStream(outStream)) {

                        byte[] buffer = new byte[4096];
                        int bytesRead;
                        while ((bytesRead = fileIn.read(buffer)) != -1) {
                            bufferedOut.write(buffer, 0, bytesRead);
                        }
                        bufferedOut.flush();
                        System.out.println("Archivo " + gameName + " enviado al cliente.");
                    } catch (IOException e) {
                        System.err.println("Error al enviar archivo: " + e.getMessage());
                    }
                } else {
                    System.out.println("Archivo no encontrado: " + gameName);
                    out.println("Juego no encontrado.");
                }
            } else {
                System.out.println("Solicitud no válida del cliente.");
                out.println("Solicitud no válida.");
            }
        } catch (IOException e) {
            System.err.println("Error en la conexión con el cliente: " + e.getMessage());
        } finally {
            try {
                socket.close();
            } catch (IOException e) {
                System.err.println("Error al cerrar socket: " + e.getMessage());
            }
        }
    }
}
