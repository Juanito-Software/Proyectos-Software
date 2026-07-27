
package com.mycompany.juanbp_ra5_app;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.interfaces.RSAKey;
import java.security.spec.MGF1ParameterSpec;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.OAEPParameterSpec;
import javax.crypto.spec.PSource;

/**
 * Cifrado y descifrado de ficheros con RSA usando relleno OAEP.
 *
 * OAEP sustituye a PKCS#1 v1.5, que es vulnerable al ataque de Bleichenbacher:
 * un atacante que pueda observar si el descifrado falla o no puede ir
 * recuperando el mensaje original a base de peticiones. OAEP no da esa señal.
 *
 * OAEP consume mas espacio de relleno que PKCS#1 (66 bytes con SHA-256 frente a
 * 11), asi que el bloque de texto en claro que cabe en cada operacion es menor.
 * Por eso el tamaño de bloque se calcula a partir del modulo de la clave en
 * lugar de estar fijado a 117 bytes.
 */
public class RSAEncryption {

    /**
     * Parametros OAEP declarados de forma explicita.
     *
     * Es intencionado: la implementacion por defecto de Java usa SHA-256 para el
     * hash pero SHA-1 para la funcion MGF1, una incoherencia historica que
     * provoca fallos de interoperabilidad dificiles de diagnosticar. Fijando
     * ambos a SHA-256 el comportamiento queda definido.
     */
    private static final OAEPParameterSpec PARAMETROS_OAEP = new OAEPParameterSpec(
            "SHA-256", "MGF1", MGF1ParameterSpec.SHA256, PSource.PSpecified.DEFAULT);

    /** Espacio que consume el relleno OAEP con SHA-256: 2 * 32 + 2 bytes. */
    private static final int SOBRECARGA_OAEP = 66;

    /** Devuelve el tamaño del modulo de la clave en bytes (128 para RSA-1024, 256 para RSA-2048). */
    private static int tamanoModulo(java.security.Key clave) {
        return ((RSAKey) clave).getModulus().bitLength() / 8;
    }

    // Metodo para encriptar un archivo usando una clave pública
    public static void encriptarRSA(PublicKey clavePublica, String rutaFichero, String rutaEncriptado){
    
        try {
            Cipher cifrar = Cipher.getInstance("RSA/ECB/OAEPPadding");

            // Inicializa el cifrador en modo encriptacion con la clave pública
            cifrar.init(Cipher.ENCRYPT_MODE, clavePublica, PARAMETROS_OAEP);

            // Tamaño maximo de texto en claro por bloque, deducido de la clave.
            int maximoPorBloque = tamanoModulo(clavePublica) - SOBRECARGA_OAEP;

            try (FileInputStream fis = new FileInputStream(new File(rutaFichero));
                 FileOutputStream fos = new FileOutputStream(new File(rutaEncriptado))) {

                byte[] bufferLectura = new byte[maximoPorBloque];
                int bufferSec;

                // Lee el archivo y encripta en bloques. Cada bloque produce
                // exactamente tamanoModulo bytes de salida, que es lo que
                // permite al descifrado volver a separarlos.
                while ((bufferSec = fis.read(bufferLectura)) != -1) {
                    byte[] bufferCifrado = cifrar.doFinal(bufferLectura, 0, bufferSec);
                    fos.write(bufferCifrado);
                }
            }

        } catch (NoSuchAlgorithmException | NoSuchPaddingException | IllegalBlockSizeException | BadPaddingException
                | InvalidAlgorithmParameterException | IOException ex) {
            Logger.getLogger(RSAEncryption.class.getName()).log(Level.SEVERE, null, ex);
        } catch (InvalidKeyException ex) {
            Logger.getLogger(RSAEncryption.class.getName()).log(Level.SEVERE, null, ex);
        }

    }
    
    // Método para desencriptar un archivo usando una clave privada
    public static void desencriptarRSA(PrivateKey clavePrivada, String rutaFichero, String rutaDesencriptado){
    
        try {
            Cipher cifrar = Cipher.getInstance("RSA/ECB/OAEPPadding");

            // Inicializa el cifrador en modo desencriptacion con la clave privada
            cifrar.init(Cipher.DECRYPT_MODE, clavePrivada, PARAMETROS_OAEP);

            // El fichero cifrado es una secuencia de bloques de exactamente
            // tamanoModulo bytes. Hay que descifrarlos uno a uno: pasarle el
            // fichero entero a doFinal solo funciona si el original cabia en un
            // unico bloque.
            int tamanoBloque = tamanoModulo(clavePrivada);

            try (FileInputStream fis = new FileInputStream(new File(rutaFichero));
                 FileOutputStream fos = new FileOutputStream(new File(rutaDesencriptado))) {

                byte[] bloque = new byte[tamanoBloque];
                int leidos;

                while ((leidos = fis.readNBytes(bloque, 0, tamanoBloque)) > 0) {
                    if (leidos != tamanoBloque) {
                        throw new IOException("El fichero cifrado esta truncado: bloque incompleto de "
                                + leidos + " bytes.");
                    }
                    // Escribe los datos desencriptados en el archivo de salida
                    fos.write(cifrar.doFinal(bloque, 0, tamanoBloque));
                }
            }

        } catch (NoSuchAlgorithmException | NoSuchPaddingException | InvalidKeyException | IllegalBlockSizeException | BadPaddingException
                | InvalidAlgorithmParameterException | IOException ex) {
            Logger.getLogger(RSAEncryption.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
