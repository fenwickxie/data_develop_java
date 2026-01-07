package com.example.dataplatform.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.orm.jpa.HibernatePropertiesCustomizer;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@Configuration
@EnableJpaRepositories(
        basePackages = "com.example.dataplatform.raw",
        entityManagerFactoryRef = "rawEntityManagerFactory",
        transactionManagerRef = "rawTransactionManager"
)
public class RawDataSourceConfig {

    @Bean
    @Primary
    @ConfigurationProperties(prefix = "spring.datasource.raw")
    public DataSource rawDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean rawEntityManagerFactory(
            @Qualifier("rawDataSource") DataSource dataSource,
            HibernatePropertiesCustomizer hibernatePropertiesCustomizer
    ) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource);
        em.setPackagesToScan("com.example.dataplatform.raw");
        em.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        Map<String, Object> props = new HashMap<>();
        hibernatePropertiesCustomizer.customize(props);
        em.setJpaPropertyMap(props);
        return em;
    }

    @Bean
    @Primary
    public JpaTransactionManager rawTransactionManager(
            @Qualifier("rawEntityManagerFactory") LocalContainerEntityManagerFactoryBean emf
    ) {
        JpaTransactionManager tx = new JpaTransactionManager();
        tx.setEntityManagerFactory(emf.getObject());
        return tx;
    }
}
