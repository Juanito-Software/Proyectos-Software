package com.example.ApiExtractData.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
// clase de configuracion
@Configuration
public class DatabaseConfig {

    @Value("${spring.datasource.url}")
    private String dbUrl;

    @Value("${spring.datasource.username}")
    private String dbUsername;

    @Value("${spring.datasource.password}")
    private String dbPassword;

    /*

       //Crea un DataSource usando DriverManagerDataSource.
       //Este DataSource se conecta a la base de datos con las credenciales
       //proporcionadas y se usa principalmente para pruebas o aplicaciones
       //de bajo tráfico, ya que no implementa pooling de conexiones.
    @Bean
    public DataSource dataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setUrl(dbUrl);
        dataSource.setUsername(dbUsername);
        dataSource.setPassword(dbPassword);
        return dataSource;
    }

     //Crea un DataSource utilizando HikariCP, que es un pool de conexiones
     //eficiente y de alto rendimiento. Este DataSource es adecuado para
     //aplicaciones en producción y puede manejar múltiples conexiones
     //simultáneamente, mejorando así el rendimiento general.
    @Bean
    public DataSource dataSource2() {
        HikariConfig hikariConfig = new HikariConfig();
        hikariConfig.setJdbcUrl(dbUrl);
        hikariConfig.setUsername(dbUsername);
        hikariConfig.setPassword(dbPassword);
        //hikariConfig.setMaximumPoolSize(10); // Configuración opcional

        return new HikariDataSource(hikariConfig);
    }

    //Para DataSource 1 o 2 (cualquiera)

    // Configura el EntityManagerFactory, que es el encargado de gestionar las entidades JPA
    // y la conexión con la base de datos.
    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory(DataSource dataSource, JpaVendorAdapter jpaVendorAdapter) {
    //public LocalContainerEntityManagerFactoryBean entityManagerFactory(@Qualifier("dataSource2") DataSource dataSource, JpaVendorAdapter jpaVendorAdapter) { //para que use el segundo y no el primero que coja
        LocalContainerEntityManagerFactoryBean factoryBean = new LocalContainerEntityManagerFactoryBean();
        factoryBean.setDataSource(dataSource);
        factoryBean.setJpaVendorAdapter(jpaVendorAdapter);
        factoryBean.setPackagesToScan("com.example.soccer.model"); // Paquete donde están tus entidades
        return factoryBean;
    }
    // Configura el JpaVendorAdapter, que es el adaptador que le dice a Spring JPA cómo interactuar con el proveedor JPA
    // En este caso, estamos usando Hibernate como el proveedor JPA
    @Bean
    public JpaVendorAdapter jpaVendorAdapter() {
        HibernateJpaVendorAdapter adapter = new HibernateJpaVendorAdapter();
        adapter.setShowSql(true); // Si quieres mostrar las consultas SQL en los logs
        adapter.setGenerateDdl(true); // Si quieres que Hibernate genere las tablas automáticamente
        adapter.setDatabasePlatform("org.hibernate.dialect.MySQLDialect"); // Dialecto específico de la base de datos
        return adapter;
    }

     */
}
