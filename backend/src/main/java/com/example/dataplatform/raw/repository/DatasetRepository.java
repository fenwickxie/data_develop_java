package com.example.dataplatform.raw.repository;

import com.example.dataplatform.raw.entity.Dataset;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DatasetRepository extends JpaRepository<Dataset, String> {
}
