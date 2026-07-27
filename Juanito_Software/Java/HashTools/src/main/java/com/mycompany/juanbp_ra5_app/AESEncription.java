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
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;


/**
 * Cifrado y descifrado de ficheros con AES en modo GCM.
 *
 * GCM (Galois/Counter Mode) es cifrado autenticado: además de ocultar el
 * contenido genera una etiqueta que permite detectar si el fichero cifrado ha
 * sido manipulado. CBC solo cifra, así que un atacante puede alterar el
 * criptograma y el descifrado no se entera.
 *
 * El nonce (equivalente al IV) se genera aleatoriamente en cada cifrado y se
 * escribe al principio del fichero, que es como debe hacerse: sin guardarlo no
 * hay forma de descifrar después, y usar siempre el mismo hace que dos ficheros
 * iguales produzcan el mismo criptograma, lo que filtra información.
 */
public class AESEncription {

    /** Longitud de nonce recomendada para GCM: 12 bytes. */
    private static final int LONGITUD_NONCE = 12;

    /** Longitud de la etiqueta de autenticación, en bits. */
    private static final int LONGITUD_TAG_BITS = 128;

    private static final SecureRandom ALEATORIO = new SecureRandom();

    //Encriptar un archivo utilizando AES
    public static void encriptarAES(String filePath, SecretKeySpec clave, String rutaEncriptado){
        try {
            // Un nonce nuevo en cada cifrado. Repetirlo con la misma clave
            // rompe por completo la seguridad de GCM.
            byte[] nonce = new byte[LONGITUD_NONCE];
            ALEATORIO.nextBytes(nonce);

            Cipher cifrar = Cipher.getInstance("AES/GCM/NoPadding");
            cifrar.init(Cipher.ENCRYPT_MODE, clave, new GCMParameterSpec(LONGITUD_TAG_BITS, nonce));

            try (FileInputStream fis = new FileInputStream(new File(filePath));
                 FileOutputStream fos = new FileOutputStream(new File(rutaEncriptado))) {

                // El nonce va al principio del fichero, en claro: no es secreto,
                // solo tiene que ser único. El descifrado lo lee de ahí.
                fos.write(nonce);

                byte[] bufferLectura = new byte[1024];
                int bufferSec;

                while((bufferSec = fis.read(bufferLectura)) != -1) {
                    byte[] bufferCifrado = cifrar.update(bufferLectura, 0, bufferSec);
                    if (bufferCifrado != null) {
                        fos.write(bufferCifrado);
                    }
                }

                // Finaliza el cifrado y escribe la etiqueta de autenticación
                fos.write(cifrar.doFinal());
            }

        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException |
                 IllegalBlockSizeException | BadPaddingException | InvalidAlgorithmParameterException | IOException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    //Desencriptar el archivo usando AES
    public static void desencriptarAES(String rutaFicheroEncriptado, SecretKeySpec clave, String rutaFicheroDesencriptado){
        try (FileInputStream fis = new FileInputStream(new File(rutaFicheroEncriptado));
             FileOutputStream fos = new FileOutputStream(new File(rutaFicheroDesencriptado))) {

            // El nonce son los primeros bytes del fichero.
            byte[] nonce = new byte[LONGITUD_NONCE];
            if (fis.read(nonce) != LONGITUD_NONCE) {
                throw new IOException("El fichero cifrado es demasiado corto: falta el nonce.");
            }

            Cipher cifrar = Cipher.getInstance("AES/GCM/NoPadding");
            cifrar.init(Cipher.DECRYPT_MODE, clave, new GCMParameterSpec(LONGITUD_TAG_BITS, nonce));

            byte[] bufferLectura = new byte[1024];
            int bufferSec;

            while((bufferSec = fis.read(bufferLectura)) != -1) {
                byte[] bufferDescifrado = cifrar.update(bufferLectura, 0, bufferSec);
                if (bufferDescifrado != null) {
                    fos.write(bufferDescifrado);
                }
            }

            // doFinal comprueba la etiqueta de autenticación: si el fichero fue
            // manipulado o la clave no es la correcta, lanza AEADBadTagException
            // en lugar de devolver datos corruptos en silencio.
            fos.write(cifrar.doFinal());

        } catch (InvalidKeyException | InvalidAlgorithmParameterException | IOException |
                 IllegalBlockSizeException | BadPaddingException | NoSuchAlgorithmException | NoSuchPaddingException ex) {
            Logger.getLogger(AESEncription.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
