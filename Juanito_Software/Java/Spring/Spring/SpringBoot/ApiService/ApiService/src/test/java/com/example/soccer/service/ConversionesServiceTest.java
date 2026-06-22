package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ConversionesServiceTest {

    private final ConversionesService conversionesService = new ConversionesService();



    @Test
    void convertirIPbinarioLongDecimalString32_ValidLong_ReturnsIPString() {
        // Dado
        long ipLong = 3232235777L; // 192.168.1.1
        String expected = "192.168.1.1";

        // Cuando
        String result = conversionesService.IpAddressLong32ToIpAddressString(ipLong);

        // Entonces
        assertEquals(expected, result);
    }

    @Test
    void convertirIPdecimalStringBinarioLong32_InvalidIP_ThrowsException() {
        // Dado
        String invalidIp = "256.0.0.1";

        // Cuando y Entonces
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            conversionesService.IpAddressStringToIpAddressLong32(invalidIp);
        });
        assertEquals("Cada octeto debe estar entre 0 y 255.", exception.getMessage());
    }
}
