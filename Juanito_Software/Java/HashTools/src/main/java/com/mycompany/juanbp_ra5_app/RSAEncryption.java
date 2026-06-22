
package com.mycompany.juanbp_ra5_app;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;

public class RSAEncryption {
    
    private static Cipher cifrar;
    
    // Metodo para encriptar un archivo usando una clave pública
    public static void encriptarRSA(PublicKey clavePublica, String rutaFichero, String rutaEncriptado){
    
        try {        
            cifrar = Cipher.getInstance("RSA/ECB/PKCS1Padding"); // Configura el cifrador RSA con ECB y Padding PKCS1
      
            cifrar.init(Cipher.ENCRYPT_MODE, clavePublica);  // Inicializa el cifrador en modo encriptacion con la clave pública
            FileInputStream fis = new FileInputStream(new File(rutaFichero));
            FileOutputStream fos = new FileOutputStream(new File(rutaEncriptado));

            byte[] bufferLectura = new byte[117];
            int bufferSec;
            
             // Lee el archivo y encripta en bloques
            while ((bufferSec = fis.read(bufferLectura)) != -1) {
                byte[] bufferCifrado = cifrar.doFinal(bufferLectura, 0, bufferSec);
                fos.write(bufferCifrado);
            }
  
        } catch (NoSuchAlgorithmException | NoSuchPaddingException | IllegalBlockSizeException | BadPaddingException 
                | IOException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        } catch (InvalidKeyException ex) {
            Logger.getLogger(RSAEncryption.class.getName()).log(Level.SEVERE, null, ex);
        }
    
    }
    
    // Método para desencriptar un archivo usando una clave privada
    public static void desencriptarRSA(PrivateKey clavePrivada, String rutaFichero, String rutaDesencriptado){
    
        try {
            cifrar = Cipher.getInstance("RSA/ECB/PKCS1Padding");
            cifrar.init(Cipher.DECRYPT_MODE, clavePrivada); // Inicializa el cifrador en modo desencriptacion con la clave privada

            FileInputStream fis = new FileInputStream(new File(rutaFichero));
            ByteArrayOutputStream baos = new ByteArrayOutputStream();

            int leerByte;
            // Lee el archivo encriptado y almacena los bytes en un ByteArrayOutputStream
            while ((leerByte = fis.read()) != -1) {
                baos.write((byte) leerByte);
            }

            byte[] data = baos.toByteArray();
            byte[] salida = cifrar.doFinal(data);

            FileOutputStream fos = new FileOutputStream(new File(rutaDesencriptado));
            fos.write(salida);// Escribe los datos desencriptados en el archivo de salida


            fis.close(); 
            fos.close(); 

        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException | IllegalBlockSizeException | BadPaddingException 
                | IOException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        }
    } 
}
