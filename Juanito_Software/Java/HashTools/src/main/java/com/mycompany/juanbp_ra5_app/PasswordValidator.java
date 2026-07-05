
package com.mycompany.juanbp_ra5_app;

import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class PasswordValidator {
    
   
    
    public static boolean validar(String password){
    
       boolean esValido;
        
       // debe contener al menos un digito, al menos una letra minúscula y una mayuscula, al menos un caracter especial, una longitud entre 8 y 20 y sin espacios
       Pattern patron = Pattern.compile("^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=?!])(?=\\S+$).{8,20}$");
       Matcher matcher = patron.matcher(password);
       esValido = matcher.matches();
       
       return esValido;
    
    }
    
}
