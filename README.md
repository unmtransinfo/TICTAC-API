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
   docker compose --env-file .env.dev -f docker-compose.dev.yml up --build
   ```

2. **Access the API:**

   - API: http://127.0.0.1:8000
   - Interactive Docs (Swagger): http://127.0.0.1:8000/docs

3. **Stop the environment:**

   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

4. **(Optional - only if you want a completely clean slate) stop and remove volumes:**
   ```bash
   docker compose -f docker-compose.dev.yml down -v
   ```

### Configuration

Environment variables are configured in [.env.dev](.env.dev):

- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` - Database configuration
- `POSTGRES_PASSWORD` - PostgreSQL superuser password
- `APP_PORT` - API port (default: 8000)

### Development Notes

#### Upgrading Dependencies

If one finds they need to update dependencies ([requirements.txt](requirements.txt)), the following steps can be followed:

1. If a new package is required, add it to [requirements.in](requirements.in)
2. Setup and activate a Python (v3.14) virtual environment. For example, with conda use:
   ```
   conda create -n tictac-api python=3.14 && conda activate tictac-api
   ```
3. Install pip-tools: `pip install pip-tools`
4. Compile new requirements: `pip-compile --upgrade`
5. (Optional) Test the update locally in your environment: `pip-sync`

_Note_: If you need to update the Python version, make sure to adjust the steps above accordingly and to update the Python image in the [Dockerfile](Dockerfile).
