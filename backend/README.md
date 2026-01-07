# data-platform-api

Spring Boot 3 skeleton for the dual-database (Raw/Metrics) architecture.

## Modules
- `Application`: bootstrap.
- `web/HealthController`: basic `/api/health` probe.
- `config`: dual DataSource + EntityManager + TxManager for raw and metrics stores.
- `raw` package: dataset + file entities, repositories, services.
- `metrics` package: metric result + report entities, repositories, services.
- `web` controllers: datasets, files, metrics, reports CRUD-style stubs.

## Config placeholders
- `spring.datasource.raw.*`: Raw DB (uploaded files metadata + OCY object location).
- `spring.datasource.metrics.*`: Metrics DB (indicator and report metadata).
- Disable `ddl-auto` in production; use Flyway/Liquibase.

## TODO
- Add security (JWT), DTO/validation, OCY signed-URL service.
- Add Flyway/Liquibase migrations for raw/metrics schemas.
- Add upload/download flows and signed URL helpers.
- Expand tests for repositories/services/controllers.

## Build
- Prereq: Java 17+, Maven 3.9+.
- `mvn clean verify` to run tests.
- `mvn spring-boot:run` to start locally (ensure both Postgres datasources are up).

## Migrations
- Flyway auto-runs for each datasource on startup via `FlywayConfig`.
- Raw DB scripts live in `db/migration/raw`; metrics DB scripts in `db/migration/metrics`.
