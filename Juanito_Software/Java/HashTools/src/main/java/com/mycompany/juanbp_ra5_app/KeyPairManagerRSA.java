/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.juanbp_ra5_app;

/**
 *
 * @author User
 */
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.logging.Level;
import java.util.logging.Logger;

public class KeyPairManagerRSA {
    
    private KeyPair clavesRSA;
    
    public KeyPairManagerRSA() { 
    }
    
    public KeyPair getClavesRSA() { 
        return clavesRSA; 
    }
    
    // Metodo para generar un par de claves RSA
    public void generarClaves(String pass, int tamaño){
    
        try { 
            KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
            SecureRandom secure = SecureRandom.getInstance("SHA1PRNG");
            secure.setSeed(pass.getBytes()); // Configura el generador aleatorio con la semilla proporcionada (password)

            clavesRSA = kpg.genKeyPair(); // Genera el par de claves
            
        } catch (NoSuchAlgorithmException ex) {
            Logger.getLogger(KeyPairManagerRSA.class.getName()).log(Level.SEVERE, null, ex); 
        }
    }
    
    // Metodo para guardar el par de claves RSA
    public void guardarClave(boolean esPrivada, String ruta){
    
        try {
            if (!esPrivada) {
                PublicKey clavePublica = getClavesRSA().getPublic();
                byte bytesClavePub[] = clavePublica.getEncoded(); // Codifica la clave pública en bytes

                FileOutputStream fos = new FileOutputStream(new File(ruta));
                fos.write(bytesClavePub);
                fos.close();               
            } else {        
                PrivateKey clavePrivada = getClavesRSA().getPrivate();
                byte bytesCPriv[] = clavePrivada.getEncoded();
                
                FileOutputStream fos = new FileOutputStream(new File(ruta));
                fos.write(bytesCPriv);
                fos.close();         
            }
        } catch (IOException ex) {
            Logger.getLogger(KeyPairManagerRSA.class.getName()).log(Level.SEVERE, null, ex);
        }
    
    }
    
    // metodo para cargar la clave publica desde un archivo
    public static PublicKey cargarClavePublica(String ruta) {
        try {
            X509EncodedKeySpec specKey = new X509EncodedKeySpec(FileToBytesReader.readBytesFichero(ruta)); // Crea la especificacion de clave publica y lee los bytes del archivo
            KeyFactory factoria = KeyFactory.getInstance("RSA");  // Obtiene la fábrica de claves RSA
            PublicKey clavePublica = factoria.generatePublic(specKey); // Genera la clave publica desde la especificación
            
            return clavePublica;
            
        } catch (IOException | NoSuchAlgorithmException | InvalidKeySpecException ex) {
            Logger.getLogger(KeyPairManagerRSA.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }

    }
    
    // metodo para cargar la clave privada
    public static PrivateKey cargarClavePrivada(String ruta) {
    
        
        try {
            PKCS8EncodedKeySpec specKey = new PKCS8EncodedKeySpec(FileToBytesReader.readBytesFichero(ruta)); // Crea la especificacion de clave privada y lee los bytes del archivo
            KeyFactory factory = KeyFactory.getInstance("RSA");
            PrivateKey clavePrivada = factory.generatePrivate(specKey);// Genera la clave privada desde la especificación
            
            return clavePrivada;
                    
        } catch (NoSuchAlgorithmException | IOException | InvalidKeySpecException ex) {
            Logger.getLogger(KeyPairManagerRSA.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }  
}
