# Podman Build and Deployment Guide

This guide provides comprehensive instructions for building and deploying the customized Open WebUI Podman image for your MSP business. Podman is a daemonless, rootless container engine that is Docker-compatible. The image includes enhanced features for software name customization, group-level API key management, and token usage tracking.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building the Podman Image](#building-the-podman-image)
- [Podman Compose Deployment](#podman-compose-deployment)
- [Podman Play Kube Deployment](#podman-play-kube-deployment)
- [Database Migration Handling](#database-migration-handling)
- [Upgrading from Existing Open WebUI](#upgrading-from-existing-open-webui)
- [Rootless Podman Configuration](#rootless-podman-configuration)
- [Testing the Deployment](#testing-the-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before building and deploying, ensure you have:

- **Podman** version 4.0 or later
- **podman-compose** (optional, for compose support) or **podman play kube** (for Kubernetes YAML)
- **Git** for cloning the repository
- At least **4GB of RAM** available for the build process
- **10GB+ free disk space** for Podman images and volumes

### Verify Prerequisites

```bash
# Check Podman version
podman --version

# Check Podman Compose (if installed)
podman-compose --version

# Verify Podman is running
podman info

# Check if running rootless
podman info | grep -i rootless
```

### Installing Podman

**On Fedora/RHEL/CentOS:**
```bash
sudo dnf install podman podman-compose
```

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install podman podman-compose
```

**On macOS:**
```bash
brew install podman
podman machine init
podman machine start
```

**On Windows:**
```bash
# Using Chocolatey
choco install podman

# Or download from: https://podman.io/getting-started/installation
```

## Building the Podman Image

### Standard Build (CPU-only)

For a standard CPU-only build suitable for most deployments:

```bash
# Clone or navigate to the repository
cd /path/to/billable-open-webui

# Build the image with a custom tag
podman build \
  --tag billable-open-webui:latest \
  --tag billable-open-webui:$(date +%Y%m%d-%H%M%S) \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build") \
  .
```

### Build with Ollama Included

To include Ollama in the same container:

```bash
podman build \
  --tag billable-open-webui:latest-ollama \
  --build-arg USE_OLLAMA=true \
  --build-arg BUILD_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "dev-build") \
  .
```

### Build with CUDA Support

For GPU-accelerated deployments (requires NVIDIA Container Toolkit):

```bash
podman build \
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

### Rootless Build Considerations

When building rootless, Podman handles user namespaces automatically. The build process is identical, but:

- Images are stored in `~/.local/share/containers/storage`
- Volumes are stored in `~/.local/share/containers/storage/volumes`
- No sudo required for most operations

### Multi-stage Build Optimization

The Dockerfile uses a multi-stage build (compatible with Podman):
1. **Frontend build stage**: Compiles the Svelte frontend
2. **Backend stage**: Sets up Python environment and dependencies

This ensures the final image only contains necessary runtime files.

## Podman Compose Deployment

### Installing podman-compose

```bash
# Using pip
pip install podman-compose

# Or using package manager
sudo dnf install podman-compose  # Fedora/RHEL
sudo apt-get install podman-compose  # Ubuntu/Debian
```

### Basic podman-compose.yaml

Create a `podman-compose.yaml` file (note: Podman Compose uses the same format as Docker Compose):

```yaml
version: '3.8'

services:
  ollama:
    image: docker.io/ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
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
      - ollama
    ports:
      - "${OPEN_WEBUI_PORT:-3000}:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/webui.db}
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

### Production podman-compose.yaml with PostgreSQL

```yaml
version: '3.8'

services:
  postgres:
    image: docker.io/postgres:15-alpine
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
    image: docker.io/ollama/ollama:latest
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

### Starting the Stack with podman-compose

```bash
# Start all services
podman-compose up -d

# View logs
podman-compose logs -f open-webui

# Check service status
podman-compose ps

# Stop all services
podman-compose down

# Stop and remove volumes (WARNING: deletes data)
podman-compose down -v
```

## Podman Play Kube Deployment

Podman can also use Kubernetes YAML files directly with `podman play kube`. This is useful for more complex deployments.

### Creating Kubernetes YAML

Create `kube-deployment.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: billable-open-webui
  labels:
    app: open-webui
spec:
  containers:
  - name: open-webui
    image: billable-open-webui:latest
    ports:
    - containerPort: 8080
      hostPort: 3000
    env:
    - name: OLLAMA_BASE_URL
      value: "http://ollama:11434"
    - name: WEBUI_SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: webui-secrets
          key: secret-key
    - name: DATABASE_URL
      value: "sqlite:///./data/webui.db"
    volumeMounts:
    - name: webui-data
      mountPath: /app/backend/data
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
  volumes:
  - name: webui-data
    hostPath:
      path: /var/lib/billable-webui/data
      type: DirectoryOrCreate
---
apiVersion: v1
kind: Secret
metadata:
  name: webui-secrets
stringData:
  secret-key: your-secret-key-here
```

### Deploying with podman play kube

```bash
# Deploy the pod
podman play kube kube-deployment.yaml

# Check pod status
podman pod ps

# View logs
podman logs billable-open-webui

# Stop and remove
podman play kube --down kube-deployment.yaml
```

## Database Migration Handling

### Automatic Migrations

The application **automatically runs database migrations** on startup, identical to Docker deployments. This is handled by the `run_migrations()` function in `backend/open_webui/config.py`.

### Migration Process

1. **On First Startup**: The migration system detects the database schema and applies all pending migrations
2. **On Upgrade**: When upgrading from an existing Open WebUI installation, only new migrations are applied
3. **Data Preservation**: All existing data is preserved during migrations

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
podman exec -it billable-open-webui bash

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
```

### Migration Troubleshooting

If migrations fail:

1. **Check Logs**:
   ```bash
   podman-compose logs open-webui | grep -i migration
   # Or with podman play kube:
   podman logs billable-open-webui | grep -i migration
   ```

2. **Verify Database Connection**:
   ```bash
   podman exec -it billable-open-webui python -c "
   from open_webui.env import DATABASE_URL
   print(f'Database URL: {DATABASE_URL}')
   "
   ```

3. **Manual Migration** (if needed):
   ```bash
   podman exec -it billable-open-webui bash
   cd /app/backend
   alembic upgrade head
   ```

## Upgrading from Existing Open WebUI

### Step-by-Step Upgrade Process

1. **Backup Your Data**:
   ```bash
   # With podman-compose volumes
   podman volume inspect billable-open-webui_webui_data
   # Backup the volume directory (usually in ~/.local/share/containers/storage/volumes/)
   
   # Or export volume data
   podman run --rm \
     -v billable-open-webui_webui_data:/data \
     -v $(pwd):/backup \
     docker.io/alpine:latest tar czf /backup/webui_backup_$(date +%Y%m%d).tar.gz -C /data .
   ```

2. **Stop Existing Container**:
   ```bash
   podman stop open-webui  # or your existing container name
   # Or with podman-compose:
   podman-compose down
   ```

3. **Update podman-compose.yaml**:
   - Change the image/build context to point to your new build
   - Ensure environment variables match your previous setup
   - Verify volume mounts are the same

4. **Start New Container**:
   ```bash
   podman-compose up -d
   # Or rebuild:
   podman-compose up -d --build
   ```

5. **Monitor Migration**:
   ```bash
   podman-compose logs -f open-webui | grep -i migration
   ```

6. **Verify Database Schema**:
   ```bash
   podman exec -it billable-open-webui python -c "
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

- **Database Compatibility**: Works with existing SQLite, PostgreSQL, and other supported databases
- **Data Preservation**: All existing user data, chats, groups, and settings are preserved
- **API Compatibility**: The API remains compatible with existing clients
- **Configuration**: Existing environment variables and config files continue to work

### Rollback Procedure

If you need to rollback:

1. **Stop New Container**:
   ```bash
   podman-compose down
   ```

2. **Restore Previous Image**:
   ```bash
   podman run -d \
     --name open-webui \
     -v webui_data:/app/backend/data \
     -p 3000:8080 \
     -e DATABASE_URL=sqlite:///./data/webui.db \
     docker.io/ghcr.io/open-webui/open-webui:main
   ```
   
   **Note**: When using `-e DATABASE_URL=...`, do NOT include a leading dash in the value. The `-e` flag itself is the dash. Use `-e DATABASE_URL="sqlite:///./data/webui.db"` not `-e DATABASE_URL="-sqlite:///./data/webui.db"`.

3. **Restore Backup** (if needed):
   ```bash
   podman run --rm \
     -v billable-open-webui_webui_data:/data \
     -v $(pwd):/backup \
     docker.io/alpine:latest sh -c "cd /data && rm -rf * && tar xzf /backup/webui_backup_YYYYMMDD.tar.gz"
   ```

## Rootless Podman Configuration

### Running Rootless

Podman's main advantage is running containers without root privileges. This is more secure and doesn't require sudo.

```bash
# Check if running rootless
podman info | grep rootless

# Should show: rootless: true
```

### Volume Locations (Rootless)

When running rootless, volumes are stored in:
- **Volumes**: `~/.local/share/containers/storage/volumes/`
- **Images**: `~/.local/share/containers/storage/`
- **Containers**: `~/.local/share/containers/storage/containers/`

### Port Binding (Rootless)

Rootless Podman uses `slirp4netns` for networking. Ports below 1024 require special configuration:

```bash
# Allow binding to privileged ports (requires root)
sudo sysctl net.ipv4.ip_unprivileged_port_start=0

# Or use ports above 1024 (recommended)
# In podman-compose.yaml, use ports like 3000:8080 instead of 80:8080
```

### User Namespace Mapping

Podman automatically handles user namespace mapping. If you need to match specific UIDs/GIDs:

```bash
# Check current subuid/subgid mapping
cat /etc/subuid
cat /etc/subgid

# Add user namespace ranges if needed
sudo usermod --add-subuids 100000-165535 $USER
sudo usermod --add-subgids 100000-165535 $USER
```

### SELinux Considerations

If SELinux is enabled (common on Fedora/RHEL):

```bash
# Check SELinux status
getenforce

# If enforcing, you may need to set proper labels
# Podman usually handles this automatically, but if issues occur:
podman run --security-opt label=disable ...
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

**Problem**: Build fails with "permission denied"
```bash
# Solution: Ensure you have proper permissions or run rootless
# Check storage location permissions
ls -la ~/.local/share/containers/storage/
```

**Problem**: Frontend build fails
```bash
# Solution: Clear build cache and rebuild
podman build --no-cache --tag billable-open-webui:latest .
```

**Problem**: Cannot pull base images
```bash
# Solution: Configure registries if behind firewall
# Edit ~/.config/containers/registries.conf
# Or use --registry flag
podman build --registry docker.io ...
```

### Runtime Issues

**Problem**: Container exits immediately
```bash
# Check logs
podman-compose logs open-webui
# Or:
podman logs billable-open-webui

# Common causes:
# - Database connection failure
# - Missing environment variables
# - Port conflicts
# - SELinux issues (check with: ausearch -m avc)
```

**Problem**: Cannot bind to port 80/443 (rootless)
```bash
# Solution: Use ports above 1024 or configure unprivileged ports
sudo sysctl net.ipv4.ip_unprivileged_port_start=0
```

**Problem**: Volume permissions issues
```bash
# Check volume ownership
podman volume inspect webui_data

# Fix permissions if needed
podman unshare chown -R $(id -u):$(id -g) /path/to/volume
```

**Problem**: Migrations not running
```bash
# Verify migration function is called
podman exec -it billable-open-webui python -c "
from open_webui.config import run_migrations
run_migrations()
"
```

**Problem**: Network connectivity issues
```bash
# Check podman network
podman network ls

# Inspect network configuration
podman network inspect podman
```

### Podman-Specific Issues

**Problem**: `podman-compose` not found
```bash
# Install podman-compose
pip install podman-compose
# Or use podman play kube instead
```

**Problem**: Containers can't communicate
```bash
# Ensure containers are on the same network
podman network ls
podman network inspect <network_name>

# Or use podman-compose which handles networking automatically
```

**Problem**: SELinux blocking access
```bash
# Check SELinux audit logs
sudo ausearch -m avc -ts recent

# Temporarily set permissive mode for testing
sudo setenforce 0

# Or configure proper SELinux policies
```

## Podman vs Docker Differences

| Feature | Docker | Podman |
|---------|--------|--------|
| Daemon | Required | Not required (daemonless) |
| Root | Often requires root | Can run rootless |
| Compose | `docker-compose` | `podman-compose` or `podman play kube` |
| Volumes | `/var/lib/docker/volumes` | `~/.local/share/containers/storage/volumes` |
| Images | `/var/lib/docker` | `~/.local/share/containers/storage` |
| Networking | Docker bridge | CNI plugins or slirp4netns (rootless) |

## Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose Documentation](https://github.com/containers/podman-compose)
- [Rootless Podman Guide](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Alembic Migration Documentation](https://alembic.sqlalchemy.org/)

## Support

For issues specific to this customized build:
1. Check the logs: `podman-compose logs -f open-webui` or `podman logs <container>`
2. Verify environment variables are set correctly
3. Ensure database migrations completed successfully
4. Review the troubleshooting section above
5. Check Podman-specific issues in the troubleshooting section

For general Open WebUI issues, refer to the [official documentation](https://docs.openwebui.com/).

