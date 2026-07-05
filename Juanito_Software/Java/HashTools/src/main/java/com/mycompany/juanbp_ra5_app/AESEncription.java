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
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;


public class AESEncription {
    
    // Vector de inicializacion (IV) de 16 bytes
    private static byte[] iv = new byte[16];
    private static IvParameterSpec ivParamSpec = new IvParameterSpec(iv);
    
    //Encriptar un archivo utilizando AES
    public static void encriptarAES(String filePath, SecretKeySpec clave, String rutaEncriptado){
        try {
            // Inicializa el cifrador en modo AES con CBC y PKCS5Padding
            Cipher cifrar = Cipher.getInstance("AES/CBC/PKCS5Padding");
            
            //Generar un vector de init (IV) aleatorio
            SecureRandom randomSec = new SecureRandom();
            randomSec.nextBytes(iv);
            
            // Inicializa el cifrador en modo de encriptación con la clave y el IV
            cifrar.init(Cipher.ENCRYPT_MODE, clave, ivParamSpec);
            
            FileInputStream fis = new FileInputStream(new File(filePath));
            FileOutputStream fos = new FileOutputStream(new File(rutaEncriptado));
            
            byte[] bufferLectura = new byte[1024];
            int bufferSec;
            
            while((bufferSec = fis.read(bufferLectura)) != -1) {
                byte[] bufferCifrado = cifrar.update(bufferLectura, 0, bufferSec);
                fos.write(bufferCifrado);
            }
            
            // Finaliza la desencriptación y escribe cualquier dato pendiente
            byte[] bytesFinal = cifrar.doFinal();
            fos.write(bytesFinal);
    
        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException | 
                 IllegalBlockSizeException | BadPaddingException | InvalidAlgorithmParameterException | IOException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    //Desencriptar el archivo usando AES
    public static void desencriptarAES(String rutaFicheroEncriptado, SecretKeySpec clave, String rutaFicheroDesencriptado){
        try {
            Cipher cifrar = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cifrar.init(Cipher.DECRYPT_MODE, clave, ivParamSpec);
            FileInputStream fis = new FileInputStream(new File(rutaFicheroEncriptado));
            FileOutputStream fos = new FileOutputStream(new File(rutaFicheroDesencriptado));
            byte[] bufferLectura = new byte[1024];
            int bufferSec;
            
            while((bufferSec = fis.read(bufferLectura)) != -1) {
                byte[] bufferEncriptado = cifrar.update(bufferLectura, 0, bufferSec);
                fos.write(bufferEncriptado);
            }
            
            byte[] bytesFinal = cifrar.doFinal();
            fos.write(bytesFinal);
            
        } catch (InvalidKeyException | InvalidAlgorithmParameterException | IOException | 
                 IllegalBlockSizeException | BadPaddingException | NoSuchAlgorithmException | NoSuchPaddingException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}