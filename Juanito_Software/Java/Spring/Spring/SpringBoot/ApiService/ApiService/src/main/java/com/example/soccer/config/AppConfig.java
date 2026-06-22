package com.example.soccer.config;

import com.example.soccer.service.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppConfig {

    @Bean
    public LenguajeAmistosoService lenguajeAmistosoService() {
        return new LenguajeAmistosoService();
    }

    @Bean
    public PseudoCifradoService pseudoCifradoService() {
        return new PseudoCifradoService();
    }

    @Bean
    public CaminandoService caminandoService() {
        return new CaminandoService();
    }

    @Bean
    public PrimosService primosService() {
        return new PrimosService();
    }

    @Bean
    public HasardService HasardService() {
        return new HasardService();
    }

    @Bean
    public ConversionesService ConversionesService() {
        return new ConversionesService();
    }

    @Bean
    public WordsCountService WordsCountService() {
        return new WordsCountService();
    }

    @Bean
    public HanoiService HanoiService() {
        return new HanoiService();
    }

    @Bean
    public HanoiService2 HanoiService2() {
        return new HanoiService2();
    }
}
