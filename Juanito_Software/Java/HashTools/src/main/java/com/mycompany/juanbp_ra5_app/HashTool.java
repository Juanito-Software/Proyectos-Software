/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.juanbp_ra5_app;

/**
 *
 * @author User
 */

import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class HashTool {
    
    // Objeto MessageDigest para calcular el hash
    private static MessageDigest mensajeDigest;
    
    // Metodo para generar un hash a partir de un texto o un archivo
    public static String generateHash(String text, String filePath, boolean isFile){
    
        try {
            if (!isFile) {             
                mensajeDigest = MessageDigest.getInstance("SHA");// Inicializa MessageDigest con el algoritmo SHA
                byte data[] = text.getBytes();
                mensajeDigest.update(data);
                byte digestResult[] = mensajeDigest.digest(); // Calcula el hash               
                String hash = ArrBytestoHexadecimal(digestResult); // Convierte el hash a formato hexadecimal
                return hash;                
            } else {
                mensajeDigest = MessageDigest.getInstance("SHA");
                byte data[] = FileToBytesReader.readBytesFichero(filePath);
                mensajeDigest.update(data);
                byte resumen[] = mensajeDigest.digest();
                
                String hash = ArrBytestoHexadecimal(resumen);
                return hash;                
            }
            
        } catch (NoSuchAlgorithmException ex) {
            Logger.getLogger(HashTool.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        } catch (IOException ex) {
            Logger.getLogger(HashTool.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    
        
    }
    
    // Metodo para convertir un array de bytes a una representacion hexadecimal
    private static String ArrBytestoHexadecimal (byte[] bytes){
        String hexa ="";
        for (int i=0; i<bytes.length; i++){
            
            String hex = Integer.toHexString(bytes[i] & 0xFF); // convierte un byte en su representación hexadecimal
            
            // Si el numero hexadecimal tiene solo un carácter le añadimos "0" al inicio para que siempre tenga dos caracteres
            if (hex.length()==1){
                hexa+="0";
            }
            hexa+=hex;
        }
        return hexa.toUpperCase();
    }
    
}
