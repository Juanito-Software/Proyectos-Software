package com.radiostack.core.domain;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class LocutorTest {

    @Test
    public void testLocutorCreationAndGetters() {
        Usuario usuario = new Usuario();
        usuario.setId(10L);
        usuario.setNombre("juanito");

        Locutor locutor = new Locutor(1L, "Juanito DJ", usuario);

        assertEquals(1L, locutor.getId());
        assertEquals("Juanito DJ", locutor.getNombreArtistico());
        assertEquals(usuario, locutor.getUsuario());
    }

    @Test
    public void testLocutorEqualsAndHashCode() {
        Locutor locutor1 = new Locutor();
        locutor1.setId(1L);

        Locutor locutor2 = new Locutor();
        locutor2.setId(1L);

        Locutor locutor3 = new Locutor();
        locutor3.setId(2L);

        assertEquals(locutor1, locutor2);
        assertNotEquals(locutor1, locutor3);
        assertEquals(locutor1.hashCode(), locutor2.hashCode());
    }
}
