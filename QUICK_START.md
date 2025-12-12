# Quick Start Guide - Customized Open WebUI

This is a quick reference for building and deploying the customized Open WebUI Docker image.

## Quick Build

```bash
# Standard build
docker build -t billable-open-webui:latest .

# Build with Ollama included
docker build --build-arg USE_OLLAMA=true -t billable-open-webui:ollama .

# Build with CUDA support
docker build --build-arg USE_CUDA=true -t billable-open-webui:cuda .
```

## Quick Deploy with Docker Compose

1. **Copy the test compose file**:
   ```bash
   cp docker-compose.test.yaml docker-compose.yaml
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start services**:
   ```bash
   docker compose up -d
   ```

4. **Check logs**:
   ```bash
   docker compose logs -f open-webui
   ```

5. **Access the UI**:
   Open http://localhost:3001 (or your configured port)

## Upgrading from Existing Open WebUI

1. **Backup your data**:
   ```bash
   docker run --rm -v <your_volume>:/data -v $(pwd):/backup \
     alpine tar czf /backup/backup.tar.gz -C /data .
   ```

2. **Update docker-compose.yaml** to use your new build

3. **Start the new container**:
   ```bash
   docker compose up -d
   ```

4. **Migrations run automatically** - watch the logs to confirm

## Verify New Features

1. **Custom Name**: Admin Settings → General → Software Name
2. **Group API Keys**: Admin → Users → Groups → Edit → API Keys tab
3. **Token Usage**: Admin → Users → See "Token Usage (30d)" column

## Troubleshooting

**Container won't start?**
```bash
docker compose logs open-webui
```

**Migrations not running?**
```bash
docker exec -it billable-test-webui python -c "from open_webui.config import run_migrations; run_migrations()"
```

**Database issues?**
```bash
# Check database connection
docker exec -it billable-test-webui python -c "from open_webui.env import DATABASE_URL; print(DATABASE_URL)"
```

For detailed documentation, see [DOCKER_BUILD_AND_DEPLOY.md](./DOCKER_BUILD_AND_DEPLOY.md)

