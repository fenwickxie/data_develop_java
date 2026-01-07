# Infrastructure templates

- `docker-compose.yml`: example wiring API + dual Postgres (raw, metrics). OCY is assumed external; a MinIO block is commented as a local stand-in.
- Set environment variables or `.env` to match credentials (JWT, OCY base URL/expiry, DB creds).

## Next steps
- Add Flyway/Liquibase migrations for Raw DB and Metrics DB.
- Provide Nginx config for frontend static hosting + API reverse proxy if needed.
- Add compose override for production image names and OCY credentials (or enable MinIO block for local).
