# Docker Build and Deployment Guide

This guide provides comprehensive instructions for building and deploying the customized Open WebUI Docker image for your MSP business. The image includes enhanced features for software name customization, group-level API key management, and token usage tracking.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building the Docker Image](#building-the-docker-image)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Database Migration Handling](#database-migration-handling)
- [Upgrading from Existing Open WebUI](#upgrading-from-existing-open-webui)
- [Testing the Deployment](#testing-the-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before building and deploying, ensure you have:

- **Docker** version 20.10 or later
- **Docker Compose** version 2.0 or later
- **Git** for cloning the repository
- At least **4GB of RAM** available for the build process
- **10GB+ free disk space** for Docker images and volumes

### Verify Prerequisites

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker info
```

## Building the Docker Image

### Standard Build (CPU-only)

For a standard CPU-only build suitable for most deployments:

```bash
# Clone or navigate to the repository
cd /path/to/billable-open-webui

# Build the image with a custom tag
docker build \
  --tag billable-open-webui:latest \
  --tag billable-open-webui:$(date +%Y%m%d-%H%M%S) \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build") \
  .
```

### Build with Ollama Included

To include Ollama in the same container:

```bash
docker build \
  --tag billable-open-webui:latest-ollama \
  --build-arg USE_OLLAMA=true \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build") \
  .
```

### Build with CUDA Support

For GPU-accelerated deployments:

```bash
docker build \
  --tag billable-open-webui:latest-cuda \
  --build-arg USE_CUDA=true \
  --build-arg USE_CUDA_VER=cu121 \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build") \
  .
```

### Build Arguments Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `USE_CUDA` | `false` | Enable CUDA support for GPU acceleration |
| `USE_CUDA_VER` | `cu128` | CUDA version (cu117, cu121, cu128) |
| `USE_OLLAMA` | `false` | Include Ollama in the container |
| `USE_SLIM` | `false` | Use slim build (excludes some models) |
| `USE_PERMISSION_HARDENING` | `false` | Enable OpenShift-compatible permissions |
| `USE_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model to use |
| `USE_RERANKING_MODEL` | `""` | Reranking model (optional) |
| `BUILD_HASH` | `dev-build` | Build identifier |
| `UID` | `0` | User ID for container (0 = root) |
| `GID` | `0` | Group ID for container (0 = root) |

### Multi-stage Build Optimization

The Dockerfile uses a multi-stage build:
1. **Frontend build stage**: Compiles the Svelte frontend
2. **Backend stage**: Sets up Python environment and dependencies

This ensures the final image only contains necessary runtime files.

## Docker Compose Deployment

### Basic docker-compose.yaml

Create a `docker-compose.yaml` file in your deployment directory:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped
    # Uncomment for GPU support
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

  open-webui:
    build:
      context: /path/to/billable-open-webui
      dockerfile: Dockerfile
      args:
        BUILD_HASH: ${BUILD_HASH:-dev-build}
    # Or use a pre-built image:
    # image: billable-open-webui:latest
    container_name: billable-open-webui
    volumes:
      - webui_data:/app/backend/data
    depends_on:
      - ollama
    ports:
      - "${OPEN_WEBUI_PORT:-3000}:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/webui.db}
      # Optional: PostgreSQL
      # - DATABASE_URL=postgresql://user:password@postgres:5432/webui
      # Optional: Custom software name (can also be set in admin UI)
      - WEBUI_NAME_CUSTOM=${WEBUI_NAME_CUSTOM:-}
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  ollama_data:
    driver: local
  webui_data:
    driver: local
```

### Production docker-compose.yaml with PostgreSQL

For production deployments with PostgreSQL:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: billable-postgres
    environment:
      POSTGRES_DB: webui
      POSTGRES_USER: webui
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change-me}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U webui"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  open-webui:
    build:
      context: /path/to/billable-open-webui
      dockerfile: Dockerfile
    image: billable-open-webui:latest
    container_name: billable-open-webui
    volumes:
      - webui_data:/app/backend/data
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_started
    ports:
      - "${OPEN_WEBUI_PORT:-3000}:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-}
      - DATABASE_URL=postgresql://webui:${POSTGRES_PASSWORD:-change-me}@postgres:5432/webui
      - WEBUI_NAME_CUSTOM=${WEBUI_NAME_CUSTOM:-Your Company Name}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  ollama_data:
    driver: local
  webui_data:
    driver: local
```

### Environment Variables File

Create a `.env` file for sensitive configuration:

```bash
# .env file
WEBUI_SECRET_KEY=your-secret-key-here
POSTGRES_PASSWORD=your-postgres-password
OPEN_WEBUI_PORT=3000
WEBUI_NAME_CUSTOM=Your Company Name
DATABASE_URL=postgresql://webui:your-postgres-password@postgres:5432/webui
```

### Starting the Stack

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f open-webui

# Check service status
docker compose ps

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v
```

## Database Migration Handling

### Automatic Migrations

The application **automatically runs database migrations** on startup. This is handled by the `run_migrations()` function in `backend/open_webui/config.py`, which is called during module import.

### Migration Process

1. **On First Startup**: The migration system detects the database schema and applies all pending migrations, including:
   - Existing Open WebUI migrations
   - New `token_usage` table migration

2. **On Upgrade**: When upgrading from an existing Open WebUI installation:
   - The system checks the current database version
   - Applies only new migrations that haven't been run
   - Preserves all existing data

### Migration Safety

The migration system is designed to be **safe for production**:

- **Idempotent**: Running migrations multiple times is safe
- **Backward Compatible**: New migrations don't break existing functionality
- **Data Preserving**: All migrations preserve existing data
- **Transactional**: Migrations run in transactions (where supported)

### Manual Migration Check

To verify migrations will run correctly:

```bash
# Enter the container
docker exec -it billable-open-webui bash

# Check current migration status
cd /app/backend
python -c "
from alembic import command
from alembic.config import Config
from open_webui.env import OPEN_WEBUI_DIR

alembic_cfg = Config(str(OPEN_WEBUI_DIR / 'alembic.ini'))
alembic_cfg.set_main_option('script_location', str(OPEN_WEBUI_DIR / 'migrations'))
command.current(alembic_cfg)
"

# View migration history
python -c "
from alembic import command
from alembic.config import Config
from open_webui.env import OPEN_WEBUI_DIR

alembic_cfg = Config(str(OPEN_WEBUI_DIR / 'alembic.ini'))
alembic_cfg.set_main_option('script_location', str(OPEN_WEBUI_DIR / 'migrations'))
command.history(alembic_cfg)
"
```

### Migration Troubleshooting

If migrations fail:

1. **Check Logs**:
   ```bash
   docker compose logs open-webui | grep -i migration
   ```

2. **Verify Database Connection**:
   ```bash
   docker exec -it billable-open-webui python -c "
   from open_webui.env import DATABASE_URL
   print(f'Database URL: {DATABASE_URL}')
   "
   ```

3. **Manual Migration** (if needed):
   ```bash
   docker exec -it billable-open-webui bash
   cd /app/backend
   alembic upgrade head
   ```

## Upgrading from Existing Open WebUI

### Step-by-Step Upgrade Process

1. **Backup Your Data**:
   ```bash
   # Backup volumes
   docker run --rm \
     -v billable-open-webui_webui_data:/data \
     -v $(pwd):/backup \
     alpine tar czf /backup/webui_backup_$(date +%Y%m%d).tar.gz -C /data .
   ```

2. **Stop Existing Container**:
   ```bash
   docker stop open-webui  # or your existing container name
   ```

3. **Update docker-compose.yaml**:
   - Change the image/build context to point to your new build
   - Ensure environment variables match your previous setup
   - Verify volume mounts are the same

4. **Start New Container**:
   ```bash
   docker compose up -d
   ```

5. **Monitor Migration**:
   ```bash
   # Watch logs for migration messages
   docker compose logs -f open-webui | grep -i migration
   ```

6. **Verify Database Schema**:
   ```bash
   # Check that token_usage table exists
   docker exec -it billable-open-webui python -c "
   from open_webui.internal.db import get_db
   from sqlalchemy import inspect
   
   with get_db() as db:
       inspector = inspect(db.bind)
       tables = inspector.get_table_names()
       if 'token_usage' in tables:
           print('✓ token_usage table exists')
       else:
           print('✗ token_usage table missing')
   "
   ```

### Compatibility Notes

- **Database Compatibility**: The new image works with existing SQLite, PostgreSQL, and other supported databases
- **Data Preservation**: All existing user data, chats, groups, and settings are preserved
- **API Compatibility**: The API remains compatible with existing clients
- **Configuration**: Existing environment variables and config files continue to work

### Rollback Procedure

If you need to rollback:

1. **Stop New Container**:
   ```bash
   docker compose down
   ```

2. **Restore Previous Image**:
   ```bash
   docker run -d \
     --name open-webui \
     -v webui_data:/app/backend/data \
     -p 3000:8080 \
     ghcr.io/open-webui/open-webui:main
   ```

3. **Restore Backup** (if needed):
   ```bash
   docker run --rm \
     -v billable-open-webui_webui_data:/data \
     -v $(pwd):/backup \
     alpine sh -c "cd /data && rm -rf * && tar xzf /backup/webui_backup_YYYYMMDD.tar.gz"
   ```

## Testing the Deployment

### Health Check

```bash
# Check if the service is running
curl http://localhost:3000/health

# Expected response:
# {"status":true}
```

### Verify New Features

1. **Custom Software Name**:
   - Log in as admin
   - Navigate to Admin Settings → General
   - Set "Software Name" to your custom name
   - Verify the name appears in the UI

2. **Group API Keys**:
   - Navigate to Admin → Users → Groups
   - Edit a group
   - Go to "API Keys" tab
   - Configure API connection settings
   - Verify users in that group use the configured API

3. **Token Usage Tracking**:
   - Navigate to Admin → Users
   - Verify "Token Usage (30d)" column appears
   - Make some chat requests
   - Check that token counts update

### Functional Tests

```bash
# Test API endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3000/api/users/admin/users/token-usage

# Test admin config endpoint
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:3000/api/auths/admin/config
```

## Troubleshooting

### Build Issues

**Problem**: Build fails with "out of memory"
```bash
# Solution: Increase Docker memory limit or use build cache
docker build --memory=8g --tag billable-open-webui:latest .
```

**Problem**: Frontend build fails
```bash
# Solution: Clear npm cache and rebuild
docker build --no-cache --tag billable-open-webui:latest .
```

### Runtime Issues

**Problem**: Container exits immediately
```bash
# Check logs
docker compose logs open-webui

# Common causes:
# - Database connection failure
# - Missing environment variables
# - Port conflicts
```

**Problem**: Migrations not running
```bash
# Verify migration function is called
docker exec -it billable-open-webui python -c "
from open_webui.config import run_migrations
run_migrations()
"
```

**Problem**: Token usage not tracking
```bash
# Verify table exists
docker exec -it billable-open-webui python -c "
from open_webui.models.token_usage import TokenUsage
from open_webui.internal.db import get_db
with get_db() as db:
    print(db.query(TokenUsage).count())
"
```

### Database Issues

**Problem**: Migration conflicts
```bash
# Check current migration version
docker exec -it billable-open-webui alembic current

# Manually upgrade if needed
docker exec -it billable-open-webui alembic upgrade head
```

**Problem**: Database locked (SQLite)
```bash
# Stop container, backup, and restart
docker compose down
# Edit database if needed
docker compose up -d
```

## Additional Resources

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Alembic Migration Documentation](https://alembic.sqlalchemy.org/)

## Support

For issues specific to this customized build:
1. Check the logs: `docker compose logs -f open-webui`
2. Verify environment variables are set correctly
3. Ensure database migrations completed successfully
4. Review the troubleshooting section above

For general Open WebUI issues, refer to the [official documentation](https://docs.openwebui.com/).

