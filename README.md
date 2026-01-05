# TICTAC API

Currently in the initial development phase.

---

## Development Setup

### Prerequisites

- Docker
- Docker Compose

### Steps

1. **Start the development environment:**

   ```bash
   docker compose --env-file .env.dev -f docker compose.dev.yml up --build
   ```

2. **Access the API:**

   - API: http://127.0.0.1:8000
   - Interactive Docs (Swagger): http://127.0.0.1:8000/docs

3. **Stop the environment:**

   ```bash
   docker compose -f docker compose.dev.yml down
   ```

4. **(Optional - only if you want a completely clean slate) stop and remove volumes:**
   ```bash
   docker compose -f docker compose.dev.yml down -v
   ```

### Configuration

Environment variables are configured in [.env.dev](.env.dev):

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` - Database configuration
- `POSTGRES_PASSWORD` - PostgreSQL superuser password
- `APP_PORT` - API port (default: 8000)
