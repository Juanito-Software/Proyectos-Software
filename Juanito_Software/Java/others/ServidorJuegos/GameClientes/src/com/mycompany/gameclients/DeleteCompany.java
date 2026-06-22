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
import db.Empresa;
import java.awt.BorderLayout;
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
import static com.mycompany.gameclients.SelectCompany.empresaSeleccionada;
import java.awt.Color;

/**
 *
 * @author User
 */

public class DeleteCompany extends javax.swing.JFrame implements Observer {
    private static final String URL = "jdbc:mysql://localhost:3306/juegos";
    private static final String USER = "root";
    private static final String PASSWORD = "";
    
    
    private JFrame statusArea;
    private JTextArea statusAreaText;
    private JPanel buttonPanel; // Panel para los botones
    private ArrayList<String> companyNames; // Lista de juegos dinámica
    private String username; // Variable para almacenar el nombre de usuario
    private String role;
    protected static String empresaSeleccionada;
    ImageIcon empresaLogo = new ImageIcon();
    private String companyName;

    
    /**
     * Creates new form Steam
     */
    
    public DeleteCompany(String username, String role) {
        
        this.username = username; // Almacenar el nombre de usuario
        this.role = role; // Almacenar el nombre de usuario
        initComponents();
        
  
        // Establecer el nombre de usuario en el JTextField
        this.jTextField1.setText(username);
        
        // Inicializar componentes personalizados
        companyNames = new ArrayList<>();
        
        buttonPanel = new JPanel();
        buttonPanel.setSize(1030, 680);
        buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));  // Para apilar botones verticalmente
        buttonPanel.setVisible(true);
        
        
        statusArea = new JFrame("Select Info");
        statusArea.setSize(400,200);
        statusArea.setLocationRelativeTo(null);
        statusAreaText=new JTextArea();
        statusArea.add(statusAreaText);
          
        // Suscribirse a GlobalState
        GlobalState.getInstance().addObserver(this);
        
 
        // Configuración del JFrame
        this.setLocationRelativeTo(null);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
              
        jPanel4.add(buttonPanel);
        jPanel4.setVisible(true);
        
        // Cargar empresas iniciales
        loadInitialCompanies(); 
    }
    
    private void loadInitialCompanies() { 
        String sql = "SELECT nombre FROM empresas";  // Cambia 'name' por el nombre de columna adecuado si es diferente

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            // Limpiar la lista antes de cargar los nuevos datos
            companyNames.clear();

            while (rs.next()) {
                // Obtener el nombre de la empresa
                companyName = rs.getString("nombre");  // Asegúrate de que 'name' corresponde al nombre de la empresa
                
                // Añadir el nombre de la empresa a la lista
                companyNames.add(companyName);
                
                // Añadir un botón para la empresa
                addButtonForCompany(companyName);
                System.out.println("Empresas cargadas correctamente: " + companyNames);
            }
            
        } catch (SQLException e) {
            statusAreaText.append("Error al cargar empresas desde la base de datos: " + e.getMessage() + "\n");
        }
    }
    
    // Método para añadir un botón para una empresa
    private void addButtonForCompany(String companyName) {
        // Obtener el logo de la empresa
        ImageIcon companyLogo = getCompanyLogo(companyName);
                
        JButton companyButton = new JButton("Eliminar " + companyName, companyLogo);
        buttonPanel.add(companyButton);
        
        // Acción del botón para ver detalles de la empresa
        companyButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                
                int confirm = JOptionPane.showConfirmDialog(
                    null,
                    "¿Está seguro de que desea eliminar la empresa " + companyName + "?",
                    "Confirmar eliminación",
                    JOptionPane.YES_NO_OPTION
                );

                if (confirm == JOptionPane.YES_OPTION) {
                    int idEmpresa=Empresa.getCompanyIdByName(companyName);
                    // Eliminar la empresa de la base de datos
                    Empresa.eliminarEmpresa(idEmpresa);
                }
            }
        });

        // Actualizar la interfaz gráfica
        buttonPanel.revalidate();
        buttonPanel.repaint();
    }
        
    // Método para obtener el logo de la empresa
    private ImageIcon getCompanyLogo(String companyName) {
        try {
            // Suponiendo que db.Empresa.getEmpresaLogoByName(companyName) devuelve un ImageIcon
            ImageIcon logo = db.Empresa.getEmpresaLogoByName(companyName);

            if (logo != null) {
                return logo;
            } else {
                System.err.println("No se encontró el logo para la empresa: " + companyName);
            }
        } catch (IOException e) {
            System.err.println("Error al leer el flujo de entrada del logo de la empresa: " + e.getMessage());
            e.printStackTrace();
        }
        // Devolver un ícono predeterminado en caso de error o si no se encontró el logo
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
        Button = new javax.swing.JButton();
        jMenuBar1 = new javax.swing.JMenuBar();

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
            .addGap(0, 1030, Short.MAX_VALUE)
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 680, Short.MAX_VALUE)
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
                .addComponent(jLabel2, javax.swing.GroupLayout.PREFERRED_SIZE, 94, javax.swing.GroupLayout.PREFERRED_SIZE)
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
                    .addComponent(jLabel2, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 23, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        BotonPanel.setBackground(new java.awt.Color(23, 29, 37));
        BotonPanel.setBorder(javax.swing.BorderFactory.createBevelBorder(javax.swing.border.BevelBorder.RAISED));
        BotonPanel.setCursor(new java.awt.Cursor(java.awt.Cursor.HAND_CURSOR));

        Button.setBackground(new java.awt.Color(23, 29, 37));
        Button.setFont(new java.awt.Font("Roboto", 0, 12)); // NOI18N
        Button.setForeground(new java.awt.Color(255, 255, 255));
        Button.setText("BACK");
        Button.setBorder(null);
        Button.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                ButtonActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout BotonPanelLayout = new javax.swing.GroupLayout(BotonPanel);
        BotonPanel.setLayout(BotonPanelLayout);
        BotonPanelLayout.setHorizontalGroup(
            BotonPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, BotonPanelLayout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(Button, javax.swing.GroupLayout.PREFERRED_SIZE, 116, javax.swing.GroupLayout.PREFERRED_SIZE))
        );
        BotonPanelLayout.setVerticalGroup(
            BotonPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, BotonPanelLayout.createSequentialGroup()
                .addGap(0, 0, Short.MAX_VALUE)
                .addComponent(Button, javax.swing.GroupLayout.PREFERRED_SIZE, 46, javax.swing.GroupLayout.PREFERRED_SIZE))
        );

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addGap(54, 54, 54)
                .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(BotonPanel, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(64, Short.MAX_VALUE))
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addComponent(jPanel2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 50, Short.MAX_VALUE)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel4, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(BotonPanel, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(46, 46, 46))
        );

        jMenuBar1.setBackground(new java.awt.Color(23, 29, 37));
        jMenuBar1.setForeground(new java.awt.Color(23, 29, 37));
        jMenuBar1.setMargin(new java.awt.Insets(0, 0, 10, 0));
        setJMenuBar(jMenuBar1);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void jTextField1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jTextField1ActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_jTextField1ActionPerformed

    private void ButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_ButtonActionPerformed
        LoggedMenu steam3 = new LoggedMenu(username,role);
        // Forzar actualización con el estado actual
        steam3.update(GlobalState.getInstance().getEmpresaSeleccionada(), GlobalState.getInstance().getEmpresaLogo());
        steam3.setVisible(true);
        this.dispose();
    }//GEN-LAST:event_ButtonActionPerformed
    
    
    /**
     * @param args the command line arguments
     */
    

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JPanel BotonPanel;
    private javax.swing.JButton Button;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JMenuBar jMenuBar1;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JTextField jTextField1;
    // End of variables declaration//GEN-END:variables

    @Override
    public void update(String empresaSeleccionada, ImageIcon empresaLogo) {
        jLabel1.setForeground(Color.WHITE); // Aquí se cambia el color del texto a blanco
        jLabel1.setText(empresaSeleccionada);
        jLabel1.setIcon(empresaLogo);
    }
}
