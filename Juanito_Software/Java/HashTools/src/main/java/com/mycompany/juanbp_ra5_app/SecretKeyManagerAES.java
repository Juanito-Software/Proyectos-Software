
package com.mycompany.juanbp_ra5_app;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.crypto.KeyGenerator;
import javax.crypto.spec.SecretKeySpec;

public class SecretKeyManagerAES {
    
    // Método para almacenar una clave AES en un archivo
    public static void almacenarClaveFichero(String password, String ruta){
        try {
            // Genera una clave AES usando la contraseña proporcionada
            SecretKeySpec key = generarClaveAES(password, 256);
            byte bytesClave []  = key.getEncoded();
            
            FileOutputStream fos = new FileOutputStream(new File(ruta));
            fos.write(bytesClave);
            fos.close();
            
        } catch (FileNotFoundException ex) {
            Logger.getLogger(SecretKeyManagerAES.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(SecretKeyManagerAES.class.getName()).log(Level.SEVERE, null, ex);
        } catch (NoSuchAlgorithmException ex) {
            Logger.getLogger(SecretKeyManagerAES.class.getName()).log(Level.SEVERE, null, ex);
        }
    
    }
    
    // Método para cargar una clave AES desde un archivo
    public static SecretKeySpec cargarKey(String ruta){
        try {
            // Lee la clave en formato de bytes desde el archivo
            byte bytesClave[] = FileToBytesReader.readBytesFichero(ruta);
            SecretKeySpec key = new SecretKeySpec(bytesClave, "AES"); // Crea una nueva instancia de SecretKeySpec con la clave leída
            
            return key;
            
        } catch (IOException ex) {
            Logger.getLogger(SecretKeyManagerAES.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }
    
    // Método para generar una clave AES usando una contraseña y un tamaño especificado
    private static SecretKeySpec generarClaveAES(String password, int size) throws NoSuchAlgorithmException{
   
        KeyGenerator kgen = KeyGenerator.getInstance("AES"); // Crea una instancia de KeyGenerator para AES
        SecureRandom secure = SecureRandom.getInstance("SHA1PRNG"); // Usa SHA1PRNG para la generación segura de números aleatorios
        secure.setSeed(password.getBytes()); // Establece la semilla para el generador de números aleatorios usando la contraseña
        kgen.init(size, secure); // Inicializa el KeyGenerator con el tamaño especificado y la semilla
        SecretKeySpec key = (SecretKeySpec) kgen.generateKey(); // Genera la clave AES
        
        return key;
    }
          
}
