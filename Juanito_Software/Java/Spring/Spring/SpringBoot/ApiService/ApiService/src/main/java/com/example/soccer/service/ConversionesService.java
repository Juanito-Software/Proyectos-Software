package com.example.soccer.service;

public class ConversionesService {


    // Convierte una dirección IP en formato de cadena decimal a un array de enteros en formato binario
    public int[] convertirIPDecimalStringBinarioArraInt(String stringIpv4) { // conversion explicita de ip decimal a binaria
        // Validación del formato de la IP
        if (stringIpv4 == null || !stringIpv4.matches("\\d+\\.\\d+\\.\\d+\\.\\d+")) { // el regex corresponde a ((1 o mas digitos) seguido de ".") 3 veces, (1 o mas digitos) 1 vez
            throw new IllegalArgumentException("Formato de IP no válido");
        }

        int decimal; // Almacena el valor decimal de cada octeto
        String binario; // Almacena el valor binario del octeto
        int intBinario = 0; // Almacena el valor binario como entero

        // Divide en octetos y almacena en un Array de String la cadena IP, separando por "."
        String[] arrStringSplit = stringIpv4.split("\\.");
        int[] arrInt = new int[arrStringSplit.length]; // Array de int para almacenar los valores binarios

        for (int i = 0; i < arrStringSplit.length; i++) { // Se itera sobre el tamaño del array de String
            decimal = Integer.parseInt(arrStringSplit[i]); // se guarda el contenido de la posicion i del array de String en la variable entera decimal y se pasa a entero
            binario = String.format("%8s", Integer.toBinaryString(decimal)).replace(' ', '0'); // Convertir el valor decimal del octeto a su representación binaria y formatear a 8 bits
            intBinario = Integer.parseInt(binario); // Se almacena el valor de binario de vuelta a la variable entera intBinario y se pasa a entero
            arrInt[i] = intBinario; // se almacena el valor en Binario en el array de enteros
        }
        return arrInt;
    }


    public String convertirIPbinarioArraIntADecimalString(int[] arrInt) {
        // Usar StringBuilder para construir la dirección IP en formato de cadena

        StringBuilder ip = new StringBuilder();
        int binario;// Variable para almacenar el valor binario en cada iteración
        int decimal;// Variable para almacenar el valor decimal convertido
        for (int i = 0; i < arrInt.length; i++) { // Recorrer cada entero en el array de enteros

            binario = arrInt[i];// Obtener el valor binario del array como entero
            decimal=convertirBinarioADecimal(binario);// Convertir de binario a decimal usando nuestro metodo
            // Agregar el valor decimal a la cadena de la IP
            ip.append(decimal);

            // Añadir un punto entre octetos, pero no después del último octeto
            if (i < arrInt.length - 1) {
                ip.append('.'); // Añadir punto solo entre octetos
            }
        }
        // Retornar la dirección IP completa como una cadena
        return ip.toString();
    }






    public int convertirDecimalABinario(int decimal) {
        int binario = 0; // Variable para almacenar el resultado binario final
        int base = 1; // La base inicia en 1, que se usará para colocar los dígitos en la posición correcta

        while (decimal > 0) { // Mientras haya cifras en el número decimal
            int residuo = decimal % 2; // Obtener el residuo de dividir el decimal entre 2 (0 o 1)
            binario += residuo * base; // Añadir el residuo a la posición correcta del número binario
            decimal /= 2; // Dividir el número decimal entre 2 para seguir con la conversión
            base *= 10; // Aumentar la base para desplazar los dígitos (de unidades a decenas, etc.)
        }

        return binario; // Retornar el número binario completo
    }

    public int convertirBinarioADecimal(int binario) {
        int decimal = 0;// Variable para almacenar el resultado decimal final
        int base = 1; // La base inicia en 1 (equivalente a 2^0), que se irá multiplicando por 2 en cada iteración

        while (binario > 0) {// Mientras haya dígitos en el número binario
            int ultimoDigito = binario % 10; // Obtener el último dígito del número binario
            // Calcular su valor decimal sumando el dígito multiplicado por su base (2^n)
            decimal += ultimoDigito * base; // Sumar el último dígito multiplicado por la base actual
            // Eliminar el último dígito del número binario
            binario /= 10; // Dividir el binario entre 10 para eliminar el último dígito
            // Multiplicar la base por 2 (esto simula 2^n en cada paso)
            base *= 2; //// Aumentar la base (es decir, la potencia de 2) para el siguiente dígito
        }
        // Retornar el valor decimal completo
        return decimal;
    }








    public String convertirIPdecimalStringBinarioString(String stringIpv4) {
        // Validación del formato de la IP: Debe ser 4 octetos separados por puntos
        if (stringIpv4 == null || !stringIpv4.matches("\\d+\\.\\d+\\.\\d+\\.\\d+")) {// el regex corresponde a ((1 o mas digitos) seguido de ".") 3 veces, (1 o mas digitos) 1 vez
            throw new IllegalArgumentException("El valor debe ser un número decimal válido");
        }

        String binario;
        StringBuilder binarioCompleto = new StringBuilder(); // Para construir la cadena binaria completa
        String[] arrStringSplit = stringIpv4.split("\\.");// Dividir la dirección IP por los puntos, obteniendo los 4 octetos

        // Iterar sobre cada octeto de la dirección IP
        for (int i = 0; i < arrStringSplit.length; i++) {
            // Convertir el octeto de String a entero (decimal)
            int octeto = Integer.parseInt(arrStringSplit[i]);

            // Validar que el valor del octeto esté en el rango 0-255
            if (octeto < 0 || octeto > 255) {
                throw new IllegalArgumentException("Cada octeto debe estar en el rango 0-255");
            }

            // Convertir el valor decimal del octeto a su representación binaria
            binario = Integer.toBinaryString(octeto);

            //formateamos a 8 bits
            String binarioOcteto = String.format("%8s", binario).replace(' ', '0');// Se almacena el contenido del String binario en la variable string binario y se pasa a String y a binario formateando para añadir 0 por la izquierda si es necesario
            // Añadir el octeto binario completo al StringBuilder
            binarioCompleto.append(binarioOcteto);

            // Añadir un punto entre los octetos (excepto después del último)
            if (i < arrStringSplit.length - 1) {
                binarioCompleto.append('.'); // Añadir punto solo entre octetos
            }
        }
        return binarioCompleto.toString(); // Devolver la cadena completa de la dirección IP en formato binario
    }

    public String convertirIPbinarioStringDecimalString(String stringBinarioIpv4) {
        // Validación del formato de la IP en binario: debe ser 4 octetos de 8 bits separados por puntos
        if (stringBinarioIpv4 == null || !stringBinarioIpv4.matches("([01]{8}\\.){3}[01]{8}")) { // El Regex corresponde a (8("0" o "1") seguido de ".") 3 veces, (8("0" y "1")) 1 vez
            throw new IllegalArgumentException("El valor debe ser una dirección IP binaria válida");
        }

        StringBuilder decimalCompleto = new StringBuilder(); // Para construir la cadena decimal completa
        String[] arrBinarioSplit = stringBinarioIpv4.split("\\."); // Dividir la dirección binaria por los puntos, obteniendo los 4 octetos

        // Iterar sobre cada octeto de la dirección binaria
        for (int i = 0; i < arrBinarioSplit.length; i++) {
            // Convertir el octeto binario a su valor decimal
            int decimal = Integer.parseInt(arrBinarioSplit[i], 2);

            // Añadir el valor decimal al StringBuilder
            decimalCompleto.append(decimal);

            // Añadir un punto entre los octetos (excepto después del último)
            if (i < arrBinarioSplit.length - 1) {
                decimalCompleto.append('.'); // Añadir punto solo entre octetos
            }
        }

        return decimalCompleto.toString(); // Devolver la cadena completa de la dirección IP en formato decimal
    }









    // Metodo para convertir una dirección IP en formato decimal (ej: "192.168.0.1") a un número entero de 32 bits
    public long IpAddressStringToIpAddressLong3222(String stringIpv4) { // Conversión implícita de IP decimal a un entero de 32 bits
        // Dividir la IP en sus cuatro octetos y almacenarla en un array de string
        String[] arrSplit = stringIpv4.split("\\.");

        // Validar que la IP contenga exactamente 4 octetos
        if (arrSplit.length != 4) {
            throw new IllegalArgumentException("La dirección IP debe contener 4 octetos.");
        }

        // Convertir cada octeto y combinar en un solo entero de 32 bits

        // Inicializar una variable para almacenar el valor de la IP como un número de 32 bits
        long ipEn32Bits = 0; // Usar un 'long' para manejar un número de 32 bits evitando problemas de signo // ej 00000000 00000000 00000000 00000000

        for (int i = 0; i < arrSplit.length; i++) {// Iterar sobre cada octeto de la dirección IP
            // Convertir el octeto de la IP de string a entero
            int octeto = Integer.parseInt(arrSplit[i]); // Convertir cada octeto a entero // ej 192

            // Validar que cada octeto esté en el rango adecuado (0-255)
            if (octeto < 0 || octeto > 255) {
                throw new IllegalArgumentException("Cada octeto debe estar entre 0 y 255.");
            }

            // Desplazar el octeto a su posición correspondiente en los 32 bits
            //ipEn32Bits |= (long) octeto << (24 - (i * 8)); // Desplazar el octeto a su posición correspondiente

            long valorDesplazar = (long)octeto; // convertimos el valor del octeto a long para evitar problemas de rango // ej = 192L

            // Calcular el desplazamiento en bits para el octeto actual
            int desplazamiento = 24 - (i * 8); // Usamos la fórmula 24 - (i * 8) para calcular la cantidad de bits que debemos desplazar el octeto. Esto asegura que el octeto se coloque en la posición correcta dentro de los 32 bits.

            long valorDesplazadoFinal = valorDesplazar << desplazamiento; // trabajando en binario, valorDesplazar se desplaza desplazamiento bits a la izquierda // ej 192L = Esto da como resultado 3221225472 en 32 bits (11000000 00000000 00000000 00000000 en binario) permite que el octeto que estamos tratando de extraer se mueva a la posición más alta (los primero 8 bits) de la representación binaria.

            //La operación |= asegura que el valor del octeto se "añada" a ipEn32Bits en la posición correcta sin sobrescribir otros valores.
            ipEn32Bits |= valorDesplazadoFinal; // Combina el valorDesplazadoFinal con el valor actual de ipEn32Bits, OR a nivel de bit
            //ej conbina 00000000 00000000 00000000 00000000 y 11000000 00000000 00000000 00000000 donde haya 0 a ambos lados=0 donde haya 1 en uno de los lados=1



            /**  iteracion 1
             * << 24 bits 11000000
             *  11000000 00000000 00000000 00000000 |= 00000000 00000000 00000000 00000000 = ipEn32Bits
             *  iteracion 2
             *  << 16 bits 10101000
             *  11000000 10101000 00000000 00000000 |= 11000000 00000000 00000000 00000000
             *  iteracion 3
             *  << 8 bits 00000000
             *  11000000 10101000 00000000 00000000 |= 11000000 10101000 00000000 00000000
             *  iteracion 4
             *  << 0 bits 00000001
             *  11000000 10101000 00000000 00000001 |= 11000000 10101000 00000000 00000001
             *  /
             *  total= 11000000 10101000 00000000 00000001 representado en numero de 32 bits
             */
        }
        return ipEn32Bits; // Devolver el valor de la dirección IP como un número de 32 bits

        // Otra forma de obtener el valor de la dirección IP en decimal es multiplicar cada octeto por la potencia de 2 correspondiente
        // 192 * 2^24 + 168 * 2^16 + 0 * 2^8 + 1 * 2^0 = 3221225473
    }

    // Metodo para convertir una dirección IP en formato decimal (ej: "192.168.0.1") a un número entero de 32 bits
    public long IpAddressStringToIpAddressLong322(String stringIpv4) {
        // Dividir la dirección IP en sus componentes
        String[] octetos = stringIpv4.split("\\."); // Utiliza una expresión regular para dividir por puntos

        // Verificar que la dirección IP tenga exactamente 4 octetos
        if (octetos.length != 4) {
            throw new IllegalArgumentException("La dirección IP no es válida");
        }

        long resultado = 0; // Variable para almacenar el valor de la dirección IP en formato entero

        // Iterar sobre cada octeto y calcular su valor correspondiente
        for (int i = 0; i < 4; i++) {
            int octeto = Integer.parseInt(octetos[i]); // Convertir el octeto de String a int
            if (octeto < 0 || octeto > 255) { // Verificar que el octeto esté en el rango válido
                throw new IllegalArgumentException("Los octetos deben estar entre 0 y 255");
            }
            // Calcular el valor del octeto multiplicado por la potencia de 256
            resultado |= (long) octeto << (8 * (3 - i)); // Usar desplazamiento de bits para construir el entero
        }

        return resultado; // Devolver el valor entero correspondiente a la dirección IP
    }











    // Metodo para convertir un número entero de 32 bits a una dirección IP en formato decimal (ej: "192.168.0.1")
    public String IpAddressLong32ToIpAddressStringgg(long ipEn32Bits) {
        // StringBuilder para construir la representación en cadena de la dirección IP
        StringBuilder ip = new StringBuilder();

        // Iterar cuatro veces, una para cada octeto (4 octetos en una dirección IP)
        for (int i = 0; i < 4; i++) {
            // Obtener cada octeto desplazando a la derecha los bits correspondientes
            // y aplicando una máscara (0xFF = 11111111) para obtener solo los últimos 8 bits (1 octeto)
            //int octeto = (int) ((ipEn32Bits >> (24 - (i * 8))) & 0xFF);

            // Calcular el desplazamiento para obtener el octeto correspondiente
            int desplazamiento = 24 - (i * 8);// Usamos la fórmula 24 - (i * 8) para calcular la cantidad de bits que debemos desplazar el octeto. Esto asegura que el octeto se coloque en la posición correcta dentro de los 32 bits.

            long resultadoDesplazado = ipEn32Bits >> desplazamiento; // trabajando en binario, ipEn32Bits se desplaza desplazamiento bits a la derecha, permite que el octeto que estamos tratando de extraer se mueva a la posición más baja (los últimos 8 bits) de la representación binaria.

            long valorEnmascarado = resultadoDesplazado & 0xFF; // Mantiene solo los 8 bits más bajos (el ultimo octeto).  AND a nivel de bit
            // ej resultadoDesplazado equivale a 00000000 00000000 00000000 11000000, 0xFF equivale a 00000000 00000000 00000000 11111111 donde haya 1 a ambos lados=1 donde haya 0 en uno de los lados=0 se mantiene 11000000

            // Convertir el valor enmascarado a int para obtener el octeto final
            int octeto = (int) valorEnmascarado;// Convertir a int para usarlo en la representación de la IP


            ip.append(octeto);// Añadir el octeto a la cadena

            // Añadir un punto después de cada octeto, excepto el último
            if (i < 3) {
                ip.append('.'); // Añadir punto solo entre octetos
            }

            /**
             * iteracion 1
             *  24 bits >> ipEn32Bits = 11000000 10101000 00000000 00000001
             *  00000000 00000000 00000000 11000000 &0xFF(nos quedamos con 11000000)
             *  11000000=192
             *  iteracion 2
             *  16 bits >> ipEn32Bits = 11000000 10101000 00000000 00000001
             *  00000000 00000000 11000000 10101000 &0xFF(nos quedamos con 10101000)
             *  10101000=168
             *  iteracion 3
             *  8 bits >> ipEn32Bits = 11000000 10101000 00000000 00000001
             *  00000000 11000000 10101000 00000000 &0xFF(nos quedamos con 00000000)
             *  00000000=0
             *  iteracion 4
             *  0 bits >> ipEn32Bits = 11000000 10101000 00000000 00000001
             *  11000000 10101000 00000000 00000001 &0xFF(nos quedamos con 00000001)
             *  00000001=1
             *   /
             *   total= 192.168.0.1
             * */
        }
        // Devolver la dirección IP en formato decimal como una cadena
        return ip.toString();
    }

    // Metodo para convertir un número entero de 32 bits a una dirección IP en formato decimal (ej: "192.168.0.1")
    public String IpAddressLong32ToIpAddressStringg(long numeroIP) {
        // Verificar que el número esté en el rango válido para una dirección IP
        if (numeroIP < 0 || numeroIP > 4294967295L) { // 2^32 - 1
            throw new IllegalArgumentException("El número debe estar en el rango de una dirección IP válida");
        }

        // Obtener cada octeto utilizando desplazamiento y AND
        StringBuilder ip = new StringBuilder();
        for (int i = 3; i >= 0; i--) {
            int octeto = (int) ((numeroIP >> (8 * i)) & 0xFF); // Desplazar y aplicar AND con 255 (0xFF)
            ip.append(octeto); // Agregar el octeto al StringBuilder
            if (i > 0) {
                ip.append("."); // Agregar un punto entre octetos
            }
        }

        return ip.toString(); // Devolver la dirección IP como String
    }


    // Metodo para convertir una dirección IP en formato decimal a un número entero de 32 bits
    public long IpAddressStringToIpAddressLong32(String stringIpv4) { // Conversión implícita de IP decimal a un entero de 32 bits
        // Dividir la dirección IP en sus cuatro octetos.
        String[] octetos = stringIpv4.split("\\.");


        // Convertir cada octeto a long y multiplicarlo por la potencia correspondiente de 256.
        long parte1 = Long.parseLong(octetos[0]) * (long) Math.pow(256, 3); // 256^3
        long parte2 = Long.parseLong(octetos[1]) * (long) Math.pow(256, 2); // 256^2
        long parte3 = Long.parseLong(octetos[2]) * (long) Math.pow(256, 1); // 256^1
        long parte4 = Long.parseLong(octetos[3]) * (long) Math.pow(256, 0); // 256^0

        // Sumar todas las partes para obtener el número como un long.
        return parte1 + parte2 + parte3 + parte4;
    }

    // Metodo para convertir un número entero de 32 bits a una dirección IP en formato decimal
    public String IpAddressLong32ToIpAddressString(long ipEn32Bits) {
        // Inicializar un StringBuilder para construir la dirección IP
        StringBuilder ip = new StringBuilder();

        // Obtener los octetos usando división y módulo
        for (int i = 0; i < 4; i++) {
            // Obtener el octeto actual(ultimo octeto)
            long octeto = ipEn32Bits % 256;
            // Insertar al principio del StringBuilder
            ip.insert(0, octeto);

            // Si no es el último octeto, añadir un punto
            if (i < 3) {
                ip.insert(0, ".");
            }

            // Actualizar ipAddress para obtener el siguiente octeto (eliminar el ultimo octeto procesado)
            ipEn32Bits /= 256;
        }

        return ip.toString();
    }

}
