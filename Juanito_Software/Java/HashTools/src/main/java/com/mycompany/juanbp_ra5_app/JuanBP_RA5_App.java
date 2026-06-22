/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 */

package com.mycompany.juanbp_ra5_app;

import java.security.PrivateKey;
import java.security.PublicKey;
import javax.crypto.spec.SecretKeySpec;

/**
 *
 * @author User
 */

public class JuanBP_RA5_App {
    public static void main(String[] args) {  
        // Inicializar el administrador de claves RSA
        KeyPairManagerRSA gerenteClavesRSA = new KeyPairManagerRSA(); 
        
        String opcionSeleccionada;
        
        // Muestra el banner de bienvenida
        Banner.bienvenida(); 
        System.out.println("");
        
        // Verifica si no hay argumentos proporcionados
        if (args.length == 0) {
            System.out.println("Escriba -h y obtendra ayuda");
            return;
        }
        
        // Obtiene la opción seleccionada del primer argumento
        opcionSeleccionada = args[0]; 

        switch (opcionSeleccionada) {   
            // Mostrar las opciones disponibles    
            case "-h":
                System.out.println("Elige una opcion de la lista:");
                System.out.println("");
                System.out.println("1 Hash Tool            ->   -ha cadena_o_fichero)");
                System.out.println("2 Generar Secret Key   ->   -gsk password ruta_guardar_clave");
                System.out.println("3 AES Encription       ->   -ae fichero_para_encriptar clave_secreta fichero_encriptado");
                System.out.println("4 AES Desencriptation  ->   -ad fichero_para_desencriptar clave_secreta fichero_desencriptado");
                System.out.println("5 Key Pair Manager RSA ->   -kpm contraseña salida_claves");
                System.out.println("6 RSA Encryption       ->   -re ruta_clave_publica fichero_para_encriptar fichero_encriptado");
                System.out.println("7 RSA Decryption       ->   -rd ruta_clave_privada fichero_para_desencriptar fichero_desencriptado");
                System.out.println("8 Digital Sign         ->   -sf ruta_clave_privada fichero_para_firmar fichero_para_firma");
                System.out.println("9 Sign Verify          ->   -vf ruta_clave_publica fichero_para_verificar firma_para_verificar");
                System.out.println("10 Salir -e");
                break;

            // Hash Tool
            case "-ha":
                String cadenaOFichero = args[1];
                try {
                    // Determina si el argumento es un archivo o un texto
                    if (new java.io.File(cadenaOFichero).exists()) {
                        String hash = HashTool.generateHash(null, cadenaOFichero, true);
                        System.out.println("Hash del fichero: " + hash);
                    } else {
                        String hash = HashTool.generateHash(cadenaOFichero, null, false);
                        System.out.println("Hash del texto: " + hash);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
                break;

            // Generar SecretKey
            case "-gsk":
                boolean valido;
                String password = args[1];
                // Valida la seguridad de la contraseña
                valido = PasswordValidator.validar(password);
                if (valido) {
                    System.out.println("Contraseña Segura");
                    String ruta = args[2];
                    // Almacena la clave secreta en un archivo
                    SecretKeyManagerAES.almacenarClaveFichero(password, ruta);
                    System.out.println("ruta para guardar la clave: " + ruta);
                } else {
                    System.out.println("La contraseña introducida no es segura.");
                }
                break;

            // AES Encription
            case "-ae":
                String rutaFicheroE = args[1];
                System.out.println("ruta del fichero a encriptar: "+rutaFicheroE);
                String rutaClave = args[2];
                System.out.println("ruta clave:"+rutaClave);
                String rutaEncriptado = args[3];
                System.out.println("ruta para el fichero encriptado: "+rutaEncriptado);
                // Carga la clave secreta y encripta el archivo
                SecretKeySpec claveSecretaE = SecretKeyManagerAES.cargarKey(rutaClave);
                AESEncription.encriptarAES(rutaFicheroE, claveSecretaE, rutaEncriptado);
                System.out.println("Fichero encriptado.");
                break;
                
            // AES Desencriptation
            case "-ad":
                String rutaFicheroD = args[1];
                System.out.println("ruta del fichero a desencriptar: "+rutaFicheroD);
                String rutaClave_2 = args[2];
                System.out.println("ruta clave: "+rutaClave_2);
                // Carga la clave secreta y desencripta el archivo
                SecretKeySpec claveSecretaD = SecretKeyManagerAES.cargarKey(rutaClave_2);
                String rutaDesencriptado = args[3];
                System.out.println("ruta para el fichero desencriptado: "+rutaDesencriptado);
                AESEncription.desencriptarAES(rutaFicheroD, claveSecretaD, rutaDesencriptado);
                System.out.println("Fichero desencriptado.");
                break;
                    
            // Key Pair Manager RSA
            case "-kpm":
                boolean valido_2;
                String pass = args[1];
                // Valida la seguridad de la contraseña
                valido_2 = PasswordValidator.validar(pass);
                if (valido_2) {
                    // Genera las claves RSA y las guarda en la ruta 
                    gerenteClavesRSA.generarClaves(pass, 256);
                    System.out.println("clave introducida"); 
                    String rutaClaves = args[2];
                    System.out.println("ruta para guardar las claves: "+rutaClaves);
                    gerenteClavesRSA.guardarClave(true, rutaClaves.concat(".pk"));
                    gerenteClavesRSA.guardarClave(false, rutaClaves.concat(".txt"));
                    System.out.println("Claves generadas");
                }else {
                    System.out.println("La password introducida no es segura.");
                }
                break;
                    
            // RSA Encryption
            case "-re":
                String rutaClavePublica = args[1];
                System.out.println("Ruta clave publica: "+rutaClavePublica);
                // Carga la clave pública y encripta el archivo
                PublicKey publicKey = KeyPairManagerRSA.cargarClavePublica(rutaClavePublica);
                
                String ficheroEn = args[2];
                System.out.println("ruta fichero a encriptar: "+ficheroEn);
                
                String rutaEn = args[3];
                System.out.println("ruta para el fichero encriptado: "+rutaEn);
                
                RSAEncryption.encriptarRSA(publicKey, ficheroEn, rutaEn);
                System.out.println("Fichero encriptado con la clave publica.");
                
                break;

            // RSA Decryption
            case "-rd":        
                String rutaClavePrivada = args[1];
                System.out.println("Ruta clave privada: "+rutaClavePrivada);
                // Carga la clave privada y desencripta el archivo
                PrivateKey privateKey = KeyPairManagerRSA.cargarClavePrivada(rutaClavePrivada);
                
                String rutaFicheroDe = args[2];
                System.out.println("ruta del fichero a desencriptar: "+rutaFicheroDe);
                
                String rutaDesencriptadoo = args[3];
                System.out.println("ruta para el fichero desencriptado: "+rutaDesencriptadoo);

                RSAEncryption.desencriptarRSA(privateKey, rutaFicheroDe, rutaDesencriptadoo);
                System.out.println("Fichero desencriptado con la clave privada.");
                break;
                
             // Digital Sign
            case "-sf":
                String rutaClavePrivadaFirma = args[1];
                System.out.println("Ruta clave privada para firmar: " + rutaClavePrivadaFirma);
                PrivateKey clavePrivadaFirma = KeyPairManagerRSA.cargarClavePrivada(rutaClavePrivadaFirma);

                String rutaFicheroFirma = args[2];
                System.out.println("Ruta del fichero a firmar: " + rutaFicheroFirma);

                String rutaFirma = args[3];
                System.out.println("Ruta para guardar la firma: " + rutaFirma);

                DigitalSign.firmarArchivo(clavePrivadaFirma, rutaFicheroFirma, rutaFirma);
                break;
                
            //  Sign Verify
            case "-vf":
                String rutaClavePublicaVerifica = args[1];
                System.out.println("Ruta clave pública para verificar: " + rutaClavePublicaVerifica);
                PublicKey clavePublicaVerificar = KeyPairManagerRSA.cargarClavePublica(rutaClavePublicaVerifica);

                String rutaFicheroVerificar = args[2];
                System.out.println("Ruta del fichero a verificar: " + rutaFicheroVerificar);

                String rutaFirmaVerificar = args[3];
                System.out.println("Ruta de la firma: " + rutaFirmaVerificar);

                DigitalSign.verificarFirma(clavePublicaVerificar, rutaFicheroVerificar, rutaFirmaVerificar);
                break;
            }
        Banner.despedida();
    }
}
