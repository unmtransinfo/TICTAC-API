# TICTAC API

Currently in the initial development phase.

## Prerequisites

- Docker
- Docker Compose

## Development Setup

### Steps

1. **(Optional):** Modify [.env.dev](.env.dev)
2. **Start the development environment:**

   ```bash
   docker compose --env-file .env.dev -f docker-compose.dev.yml --profile default up --build
   ```

   - Note: if you don't want to launch the UI (just DB+API), then use:

   ```bash
   docker compose --env-file .env.dev -f docker-compose.dev.yml --profile backend up --build
   ```

3. **Access the API:**
   - API: http://127.0.0.1:8000
   - Interactive Docs (Swagger): http://127.0.0.1:8000/docs

4. **Stop the environment:**

   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

5. **(Optional - only if you want a completely clean slate) stop and remove volumes:**
   ```bash
   docker compose -f docker-compose.dev.yml down -v
   ```

### Configuration

Environment variables are configured in [.env](.env):

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

## Production Setup (on habanero)

### Launching API

1. **Pull latest changes (for compose file mainly):**

```bash
git pull
```

2. **Copy [.env.prod.example](.env.prod.example) to `.env`**:

```bash
cp .env.prod.example .env
```

2. **Modify `.env`**
3. **(If services previously up):**

   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

4. **Pull latest images and run:**

   ```bash
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d --remove-orphans
   ```

5. **Verify deployment:**

   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs api
   ```

6. **(One-time setup) If not done so already, modify your `/etc/apache2/sites-available/` files to include the following lines:**

```
# TICTAC API (proxy rules BEFORE the Alias so they take priority)
ProxyPass /tictac/apidocs http://localhost:<APP_PORT>/docs
ProxyPassReverse /tictac/apidocs http://localhost:<APP_PORT>/docs
ProxyPass /tictac/openapi.json http://localhost:<APP_PORT>/openapi.json
ProxyPassReverse /tictac/openapi.json http://localhost:<APP_PORT>/openapi.json

ProxyPass /tictac/api/ http://localhost:<APP_PORT>/api/
ProxyPassReverse /tictac/api/ http://localhost:<APP_PORT>/api/

# TICTAC UI - serve static files from the container volume

Alias /tictac /var/www/tictac-ui/

<Directory /var/www/tictac-ui>
   Options -Indexes +FollowSymLinks
   AllowOverride None
   Require all granted

   # SPA fallback: if the file/dir doesn't exist, serve index.html

   RewriteEngine On
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^ index.html [L]
</Directory>
```

Then reload apache:

```bash
sudo apache2ctl configtest # make sure syntax ok
sudo systemctl reload apache2
curl -I https://habanero.health.unm.edu/tictac/apidocs # should give HTTP/1.1 200
```

The API docs should now be accessible at:

https://habanero.health.unm.edu/tictac/apidocs

## Pushing API to dockerhub

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
