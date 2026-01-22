# TICTAC API

Currently in the initial development phase.

---

## Production Setup (on habanero)

### Launching API

1. **(Recommended) Modify [.env](.env)**
2. **(If services previously up):**

   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

3. **Pull latest images and run:**

   ```bash
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d --remove-orphans
   ```

4. **Verify deployment:**

   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs api
   ```

5. **(One-time setup) If not done so already, modify `/etc/apache2/sites-available/000-default-le-ssl.conf` to include the following lines:**

   ```
   ProxyPreserveHost On
   ProxyPass /tictac/apidocs http://localhost:<APP_PORT>/ # modify <APP_PORT> to match your .env file
   ProxyPassReverse /tictac/apidocs http://localhost:<APP_PORT>/
   ```

   Then restart apache:

   ```
   sudo systemctl restart apache2
   ```

The API docs should now be accessible at:

https://habanero.health.unm.edu/tictac/apidocs

### Pushing API to dockerhub

1. **Build image:**

   ```
   docker build -t unmtransinfo/tictac_api:latest .
   ```

2. **Add tags to image:**

   ```
   docker tag unmtransinfo/tictac_api:latest unmtransinfo/tictac_api:v1 # modify v1 to whatever version you want to use
   ```

3. **Login**:

   ```
   docker login
   ```

4. **Push**:

   ```
   docker push unmtransinfo/tictac_api:latest && docker push unmtransinfo/tictac_api:v1
   ```

## Development Setup

### Prerequisites

- Docker
- Docker Compose

### Steps

1. **Start the development environment:**

   ```bash
   docker compose -f docker-compose.dev.yml up --build
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

#### Code Formatting with Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) hooks to automatically format Python code with [Black](https://black.readthedocs.io/) before each commit. This ensures consistent code style across the project.

**Setup (one-time):**

1. Setup and activate a Python (v3.14) virtual environment if you haven't already:

   ```bash
   conda create -n tictac-api python=3.14 && conda activate tictac-api
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install the pre-commit hooks:
   ```bash
   pre-commit install
   ```

**Usage:**

Once installed, the hooks will run automatically on `git commit`. If Black reformats any files, the commit will be aborted and you'll need to:

1. Review the changes Black made
2. Stage the reformatted files: `git add <files>`
3. Commit again: `git commit`

**Manual formatting:**

You can also run Black manually on all files:

```bash
black .
```

Or run all pre-commit hooks manually without committing:

```bash
pre-commit run --all-files
```

**Configuration:**

- Pre-commit hooks are configured in [.pre-commit-config.yaml](.pre-commit-config.yaml)
