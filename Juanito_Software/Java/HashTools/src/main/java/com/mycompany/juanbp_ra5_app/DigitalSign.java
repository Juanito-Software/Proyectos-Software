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
import java.security.InvalidKeyException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.SignatureException;
import java.security.NoSuchAlgorithmException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class DigitalSign {
    
    // Método para firmar un archivo usando una clave privada
    public static void firmarArchivo(PrivateKey clavePrivada, String rutaFichero, String rutaFirma) {
        try {
            Signature firma = Signature.getInstance("SHA256withRSA");
            firma.initSign(clavePrivada);

            FileInputStream fis = new FileInputStream(new File(rutaFichero));
            byte[] bufferLectura = new byte[1024];
            int len;
            while ((len = fis.read(bufferLectura)) != -1) {
                firma.update(bufferLectura, 0, len);
            }
            fis.close();

            byte[] firmaBytes = firma.sign();

            FileOutputStream fos = new FileOutputStream(new File(rutaFirma));
            fos.write(firmaBytes);
            fos.close();

            System.out.println("Archivo firmado exitosamente.");

        } catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException | IOException ex) {
            Logger.getLogger(DigitalSign.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    // Método para verificar la firma de un archivo usando una clave pública
    public static boolean verificarFirma(PublicKey clavePublica, String rutaFichero, String rutaFirma) {
        try {
            Signature firma = Signature.getInstance("SHA256withRSA");
            firma.initVerify(clavePublica);

            FileInputStream fis = new FileInputStream(new File(rutaFichero));
            byte[] bufferLEctura = new byte[1024];
            int size;
            while ((size = fis.read(bufferLEctura)) != -1) {
                firma.update(bufferLEctura, 0, size);
            }
            fis.close();

            FileInputStream fisFirma = new FileInputStream(new File(rutaFirma));
            byte[] firmaBytes = new byte[fisFirma.available()];
            fisFirma.read(firmaBytes);
            fisFirma.close();

            boolean verificado = firma.verify(firmaBytes);

            if (verificado) {
                System.out.println("Firma verificada correctamente.");
            } else {
                System.out.println("La firma no es válida.");
            }

            return verificado;

        } catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException | IOException ex) {
            Logger.getLogger(DigitalSign.class.getName()).log(Level.SEVERE, null, ex);
            return false;
        }
    }
}
