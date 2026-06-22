package com.example.scheduledbach.writer;


import com.example.scheduledbach.models.Venta;
import com.example.scheduledbach.repository.VentaRepository;
import com.example.scheduledbach.repository.VentaRepositoryTertiary;
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

@Service
@Component
public class VentaItemWriter implements ItemWriter<Venta> {

    // Inyección de EntityManagerFactory
    private final EntityManagerFactory entityManagerFactory;

    public VentaItemWriter(@Qualifier("entityManagerFactoryTertiary") EntityManagerFactory entityManagerFactory) {
        this.entityManagerFactory = entityManagerFactory;
    }

    @Override
    public void write(Chunk<? extends Venta> chunk) throws Exception {
        // Creamos el EntityManager para interactuar con la tercera base de datos
        EntityManager entityManager = entityManagerFactory.createEntityManager();
        entityManager.getTransaction().begin(); // Inicia la transacción

        try {
            System.out.println("Guardando un chunk de " + chunk.size() + " ventas");

            for (Venta venta : chunk) {
                // Verificamos si la venta ya existe en la base de datos
                if (entityManager.find(Venta.class, venta.getId()) == null) {
                    System.out.println("Guardando venta con id: " + venta.getId());
                    entityManager.persist(venta);  // Guarda la venta si no existe
                } else {
                    System.out.println("La venta con id: " + venta.getId() + " ya existe, no se guardará.");
                }
            }

            entityManager.getTransaction().commit();  // Realiza el commit de la transacción
        } catch (Exception e) {
            entityManager.getTransaction().rollback();  // Si ocurre un error, deshace la transacción
            throw e;
        } finally {
            entityManager.close();  // Cierra el EntityManager
        }
    }
}