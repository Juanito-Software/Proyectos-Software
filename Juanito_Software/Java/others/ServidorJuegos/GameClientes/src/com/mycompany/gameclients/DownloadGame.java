/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/GUIForms/JFrame.java to edit this template
 */

package com.mycompany.gameclients;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

import com.mycompany.gameclients.AddGame;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.FlowLayout;
import java.awt.image.BufferedImage;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.net.SocketException;
import java.util.ArrayList;
import javax.swing.JPanel;
import org.netbeans.lib.awtextra.AbsoluteLayout;
import java.sql.*;
import javax.swing.JOptionPane;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import javax.imageio.ImageIO;
import javax.swing.BoxLayout;
import javax.swing.JLabel;

/**
 *
 * @author User
 */

public class DownloadGame extends javax.swing.JFrame implements Observer{
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";
    
    private static final String SERVER_ADDRESS = "localhost"; // Dirección del servidor
    private static final int SERVER_PORT = 12345; // Puerto del servidor
    
    private JFrame statusArea;
    private JTextArea statusAreaText;
    private JPanel buttonPanel; // Panel para los botones
    private ArrayList<String> gameNames; // Lista de juegos dinámica
    private String username; // Variable para almacenar el nombre de usuario
    private String role;
    private String gameName;
    private static String gameName2;
    
    /**
     * Creates new form Steam
     */
    
    public DownloadGame(String username, String role) {
        
        this.username = username; // Almacenar el nombre de usuario
        this.role = role; // Almacenar el role de usuario
        
        initComponents();
        
        // Evitar que la ventana sea redimensionable
        //setResizable(false);
        // Suscribirse a GlobalState
        GlobalState.getInstance().addObserver(this);
        
        // Establecer el nombre de usuario en el JTextField
        this.jTextField1.setText(username);
        
        // Inicializar componentes personalizados
        gameNames = new ArrayList<>();
        
        buttonPanel = new JPanel();
        buttonPanel.setSize(1030, 680);
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));  // Para apilar botones verticalmente
        buttonPanel.setVisible(true);
        
        
        statusArea = new JFrame("Download Info");
        statusArea.setSize(400,200);
        statusArea.setLocationRelativeTo(null);
        statusAreaText=new JTextArea();
        statusArea.add(statusAreaText);
          

            
        // Configuración del JFrame
        this.setLocationRelativeTo(null);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            
            
        // Cargar juegos iniciales
        loadInitialGames(); 
            

        jPanel4.setLayout(new BorderLayout()); // Cambiar el layout para que soporte scroll
        jPanel4.add(buttonPanel, BorderLayout.CENTER);
        jPanel4.setVisible(true);        
    }
    
    private void loadInitialGames() {
        String sql = "SELECT name FROM games";  // Cambia 'name' por el nombre de columna adecuado si es diferente

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            // Limpiar la lista antes de cargar los nuevos datos
            gameNames.clear();

            while (rs.next()) {
                // Obtener el nombre del juego
                gameName = rs.getString("name");  // Asegúrate de que 'name' corresponde al nombre del juego
                
                // Añadir el nombre del juego a la lista
                gameNames.add(gameName);
                
                gameName2=gameName;
                
                // Añadir un botón para el juego
                addButtonForGame(gameName);
                System.out.println("Juegos cargados correctamente: " + gameName);
            }

        } catch (SQLException e) {
            statusAreaText.append("Error al cargar juegos desde la base de datos: " + e.getMessage() + "\n");
        }
    }
    
    // Método para añadir un botón para un juego
    private void addButtonForGame(String gameName) {
        // Obtener el logo del juego
        ImageIcon gameLogo = getGameLogo(gameName);
                
        JButton gameButton = new JButton("Descargar " + gameName, gameLogo);
        buttonPanel.add(gameButton);
        
        // Acción del botón para descargar el juego
        gameButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Asumimos que los archivos a descargar son .zip
                String fileName = gameName + ".zip";
                Path destinationPath = Paths.get(System.getProperty("user.home"), "Desktop", fileName);
                statusArea.setVisible(true);
                downloadGame(fileName, destinationPath, statusAreaText,username);
            }
        });        

        // Actualizar la interfaz gráfica
        buttonPanel.revalidate();
        buttonPanel.repaint();
    }    
        
    public static void downloadGame(String gameName, Path destinationPath, JTextArea statusArea, String UserName) {
        new Thread(() -> {
            try (Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
                 PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                 InputStream in = socket.getInputStream();
                 OutputStream fileOut = new FileOutputStream(destinationPath.toFile())) {
                
                
                // Configurar SO_LINGER
                try {
                    socket.setSoLinger(true, 10);
                } catch (SocketException e) {
                    statusArea.append("Error al configurar SO_LINGER: " + e.getMessage() + "\n");
                }
                
                
                // Enviar solicitud de descarga
                statusArea.append("Enviando solicitud para descargar: " + gameName + "\n");
                out.println("DESCARGAR " + gameName);

                // Leer la respuesta del servidor y guardar el archivo
                byte[] buffer = new byte[4096];
                int bytesRead;
                while ((bytesRead = in.read(buffer)) != -1) {
                    fileOut.write(buffer, 0, bytesRead);
                }

                statusArea.append("Descarga completa.\n");
                
                // Registrar la descarga en el archivo de historial con fecha y hora
                LocalDateTime now = LocalDateTime.now();
                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
                
                int gameID=db.Game.getGameIdByName(gameName2);
                int usernameID=db.User.getUserIdByUsername(UserName);
                db.Descarga.registrarDescarga(usernameID, gameID, now.format(formatter));

                try (BufferedWriter writer = new BufferedWriter(new FileWriter("download_history.txt", true))) {
                    writer.write(gameName + " - " + now.format(formatter) + "\n");
                } catch (IOException e) {
                    statusArea.append("Error al guardar el historial de descargas: " + e.getMessage() + "\n");
                    e.printStackTrace();
                }
                    } catch (IOException e) {
                        statusArea.append("Error al descargar el juego: " + e.getMessage() + "\n");
                    }
        }).start();
    }
    
    // Método que puedes llamar cuando se añade un nuevo juego desde la interfaz
    public void onNewGameAdded(String newGameName) {
        gameNames.add(newGameName);
        addButtonForGame(newGameName);
    }
    
    private ImageIcon getGameLogo(String gameName) {
        // Aquí se implementa la lógica para recuperar el logo del juego desde la base de datos
        // y convertirlo en un ImageIcon.

        try {
            // Suponiendo que db.Game.getGameLogoByName(gameName) devuelve un Blob
            Blob logoBlob = db.Game.getGameLogoByName(gameName);

            if (logoBlob != null) {
                // Obtener el flujo de entrada del Blob
                InputStream inputStream = logoBlob.getBinaryStream();

                // Leer la imagen desde el flujo de entrada
                BufferedImage bufferedImage = ImageIO.read(inputStream);

                // Convertir la imagen en un ImageIcon
                if (bufferedImage != null) {
                    return new ImageIcon(bufferedImage);
                } else {
                    // Si la imagen no se pudo leer correctamente, devolver un ícono predeterminado
                    System.err.println("No se pudo leer la imagen del logo para el juego: " + gameName);
                }
            } else {
                System.err.println("No se encontró el logo para el juego: " + gameName);
            }
        } catch (SQLException e) {
            System.err.println("Error al recuperar el logo del juego desde la base de datos: " + e.getMessage());
            e.printStackTrace();
        } catch (IOException e) {
            System.err.println("Error al leer el flujo de entrada del logo del juego: " + e.getMessage());
            e.printStackTrace();
    }
        return null;
    }

    
    
    
    
    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jPanel3 = new javax.swing.JPanel();
        jPanel1 = new javax.swing.JPanel();
        jPanel4 = new javax.swing.JPanel();
        jPanel2 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        jTextField1 = new javax.swing.JTextField();
        jLabel5 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        BotonPanel = new javax.swing.JPanel();
        jButton = new javax.swing.JButton();

        javax.swing.GroupLayout jPanel3Layout = new javax.swing.GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 100, Short.MAX_VALUE)
        );
        jPanel3Layout.setVerticalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 100, Short.MAX_VALUE)
        );

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setBackground(new java.awt.Color(27, 40, 56));

        jPanel1.setBackground(new java.awt.Color(26, 41, 58));

        jPanel4.setForeground(new java.awt.Color(153, 153, 153));

        javax.swing.GroupLayout jPanel4Layout = new javax.swing.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 1087, Short.MAX_VALUE)
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 416, Short.MAX_VALUE)
        );

        jPanel2.setBackground(new java.awt.Color(23, 29, 37));

        jLabel1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/Images/steam.png"))); // NOI18N

        jTextField1.setEditable(false);
        jTextField1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jTextField1ActionPerformed(evt);
            }
        });

        jLabel5.setIcon(new javax.swing.ImageIcon(getClass().getResource("/Images/User.png"))); // NOI18N

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addGap(57, 57, 57)
                .addComponent(jLabel1)
                .addGap(18, 18, 18)
                .addComponent(jLabel2, javax.swing.GroupLayout.PREFERRED_SIZE, 102, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel5, javax.swing.GroupLayout.PREFERRED_SIZE, 113, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addGap(12, 12, 12)
                        .addComponent(jTextField1, javax.swing.GroupLayout.PREFERRED_SIZE, 89, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(35, 35, 35))
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel2Layout.createSequentialGroup()
                .addComponent(jLabel5, javax.swing.GroupLayout.PREFERRED_SIZE, 69, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jTextField1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(0, 0, Short.MAX_VALUE))
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel2Layout.createSequentialGroup()
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel1, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 62, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel2, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 26, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        BotonPanel.setBackground(new java.awt.Color(23, 29, 37));
        BotonPanel.setBorder(javax.swing.BorderFactory.createBevelBorder(javax.swing.border.BevelBorder.RAISED));
        BotonPanel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        jButton.setBackground(new java.awt.Color(23, 29, 37));
        jButton.setFont(new java.awt.Font("Roboto", 0, 12)); // NOI18N
        jButton.setForeground(new java.awt.Color(255, 255, 255));
        jButton.setText("BACK");
        jButton.setBorder(null);
        jButton.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout BotonPanelLayout = new javax.swing.GroupLayout(BotonPanel);
        BotonPanel.setLayout(BotonPanelLayout);
        BotonPanelLayout.setHorizontalGroup(
            BotonPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, BotonPanelLayout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(jButton, javax.swing.GroupLayout.PREFERRED_SIZE, 116, javax.swing.GroupLayout.PREFERRED_SIZE))
        );
        BotonPanelLayout.setVerticalGroup(
            BotonPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, BotonPanelLayout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(jButton, javax.swing.GroupLayout.PREFERRED_SIZE, 46, javax.swing.GroupLayout.PREFERRED_SIZE))
        );

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(BotonPanel, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(67, 67, 67))
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addGap(54, 54, 54)
                .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(145, Short.MAX_VALUE))
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addComponent(jPanel2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(184, 184, 184)
                .addComponent(BotonPanel, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(110, 110, 110))
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, 770, Short.MAX_VALUE)
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void jTextField1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jTextField1ActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_jTextField1ActionPerformed

    private void jButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonActionPerformed
        LoggedMenu steam3 = new LoggedMenu(username, role);
        steam3.update(GlobalState.getInstance().getEmpresaSeleccionada(), GlobalState.getInstance().getEmpresaLogo());
        steam3.setVisible(true);
        this.dispose();
    }//GEN-LAST:event_jButtonActionPerformed
    
    
    /**
     * @param args the command line arguments
     */
    

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JPanel BotonPanel;
    private javax.swing.JButton jButton;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JTextField jTextField1;
    // End of variables declaration//GEN-END:variables

    @Override
    public void update(String empresaSeleccionada, ImageIcon empresaLogo) {
        jLabel2.setForeground(Color.WHITE); // Aquí se cambia el color del texto a blanco
        jLabel2.setText(empresaSeleccionada);
        jLabel1.setIcon(empresaLogo);
    }
}
