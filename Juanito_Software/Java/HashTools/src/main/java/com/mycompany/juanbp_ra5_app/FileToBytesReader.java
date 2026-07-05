/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.juanbp_ra5_app;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author User
 */

// Clase para la lectura de bytes de un archivo
public class FileToBytesReader  {
    
        private static FileInputStream fis;
        private static ByteArrayOutputStream bos = new ByteArrayOutputStream();
        
        // Metodo para leer bytes de un archivo
        public static byte[] readBytesFichero(String rutaFichero) throws IOException {

            File file = new File(rutaFichero);
            byte bufferLectura[] = new byte[1024];
            int readBytes;

            try {
                fis = new FileInputStream(file);
            } catch (FileNotFoundException ex) {
                Logger.getLogger(FileToBytesReader.class.getName()).log(Level.SEVERE, null, ex);
            }

            while ((readBytes = fis.read(bufferLectura)) != -1) {
                bos.write(bufferLectura, 0, readBytes);
            }

            byte data[] = bos.toByteArray();       
            return data;
        }
    }   