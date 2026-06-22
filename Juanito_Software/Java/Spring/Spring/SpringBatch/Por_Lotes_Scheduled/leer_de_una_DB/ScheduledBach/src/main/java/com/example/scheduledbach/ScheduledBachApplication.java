package com.example.scheduledbach;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(exclude={DataSourceAutoConfiguration.class})
@EnableJpaRepositories(basePackages = "com.example.scheduledbach.repository")
@EntityScan(basePackages = "com.example.scheduledbach.models")
public class ScheduledBachApplication {

	public static void main(String[] args) {
		SpringApplication.run(ScheduledBachApplication.class, args);
	}

}
