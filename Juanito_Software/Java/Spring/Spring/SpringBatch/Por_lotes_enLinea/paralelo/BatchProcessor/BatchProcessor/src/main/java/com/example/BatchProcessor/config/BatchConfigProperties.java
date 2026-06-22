package com.example.BatchProcessor.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

// Clase para almacenar las properties definidas en el fichero application.properties
@Configuration
@ConfigurationProperties(prefix = "batch.config") // El prefijo "batch.config" asegura que solo las propiedades de este prefijo sean mapeadas
public class BatchConfigProperties {

    private BatchConfig batch = new BatchConfig(); // Solo se mapean las propiedades bajo "batch.config.batch"

    // Getters y Setters

    public BatchConfig getBatch() {
        return batch;
    }

    public void setBatch(BatchConfig batch) {
        this.batch = batch;
    }

    public static class BatchConfig {
        private boolean jobEnabled;
        private String initializeSchema;
        private String tablePrefix;

        // Getters y Setters

        public boolean isJobEnabled() {
            return jobEnabled;
        }

        public void setJobEnabled(boolean jobEnabled) {
            this.jobEnabled = jobEnabled;
        }

        public String getInitializeSchema() {
            return initializeSchema;
        }

        public void setInitializeSchema(String initializeSchema) {
            this.initializeSchema = initializeSchema;
        }

        public String getTablePrefix() {
            return tablePrefix;
        }

        public void setTablePrefix(String tablePrefix) {
            this.tablePrefix = tablePrefix;
        }
    }
}
