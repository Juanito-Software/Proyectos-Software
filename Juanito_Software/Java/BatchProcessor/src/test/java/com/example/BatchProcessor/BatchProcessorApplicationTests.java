package com.example.BatchProcessor;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * Arranque del contexto de Spring.
 *
 * <p>Es el test que genera Spring Initializr y durante mucho tiempo no se
 * ejecuto en ninguna parte: {@code @SpringBootTest} levanta el contexto
 * completo, y la configuracion principal apunta a un MySQL en
 * localhost:3306. Sin esa base de datos delante el contexto no arranca, asi
 * que el test solo pasaba en la maquina de quien tuviera el servidor
 * levantado y el CI lo saltaba con {@code -DskipTests}.
 *
 * <p>El perfil {@code test} lo redirige a H2 en memoria. Con eso se ejecuta
 * en cualquier sitio, incluido un runner de CI sin nada instalado.
 *
 * <p>Lo que comprueba, dicho sin adornos: que todos los beans se construyen y
 * se inyectan entre si. No prueba ninguna regla de negocio. En una aplicacion
 * que resuelve entidades por reflexion y compone Job y Step en tiempo de
 * ejecucion, eso igualmente detecta cableado roto, propiedades que faltan y
 * configuracion invalida, que es mas de lo que parece para un test de una
 * linea.
 */
@SpringBootTest
@ActiveProfiles("test")
class BatchProcessorApplicationTests {

	@Test
	void contextLoads() {
	}

}
