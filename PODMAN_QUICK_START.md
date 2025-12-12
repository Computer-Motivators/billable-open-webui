# Podman Quick Start Guide - Customized Open WebUI

This is a quick reference for building and deploying the customized Open WebUI Podman image.

## Quick Build

```bash
# Standard build
podman build -t billable-open-webui:latest .

# Build with Ollama included
podman build --build-arg USE_OLLAMA=true -t billable-open-webui:ollama .

# Build with CUDA support
podman build --build-arg USE_CUDA=true -t billable-open-webui:cuda .
```

## Quick Deploy with Podman Compose

1. **Install podman-compose** (if not already installed):
   ```bash
   pip install podman-compose
   # Or: sudo dnf install podman-compose  # Fedora/RHEL
   ```

2. **Copy the test compose file**:
   ```bash
   cp podman-compose.test.yaml podman-compose.yaml
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start services**:
   ```bash
   podman-compose up -d
   ```

5. **Check logs**:
   ```bash
   podman-compose logs -f open-webui
   ```

6. **Access the UI**:
   Open http://localhost:3001 (or your configured port)

## Quick Deploy with Podman (without compose)

1. **Start Ollama**:
   ```bash
   podman run -d \
     --name ollama \
     -v ollama_data:/root/.ollama \
     -p 11434:11434 \
     docker.io/ollama/ollama:latest
   ```

2. **Start Open WebUI**:
   ```bash
   podman run -d \
     --name billable-webui \
     -v webui_data:/app/backend/data \
     -p 3000:8080 \
     --add-host=host.docker.internal:host-gateway \
     -e OLLAMA_BASE_URL=http://ollama:11434 \
     -e WEBUI_SECRET_KEY=your-secret-key \
     -e DATABASE_URL=sqlite:///./data/webui.db \
     billable-open-webui:latest
   ```
   
   **Important**: When setting `DATABASE_URL`, do NOT include a leading dash. Use:
   - ✅ Correct: `-e DATABASE_URL="sqlite:///./data/webui.db"`
   - ❌ Wrong: `-e DATABASE_URL="-sqlite:///./data/webui.db"` (leading dash)

3. **Check status**:
   ```bash
   podman ps
   podman logs -f billable-webui
   ```

## Upgrading from Existing Open WebUI

1. **Backup your data**:
   ```bash
   # Find volume location
   podman volume inspect <volume_name>
   
   # Backup (adjust path based on volume location)
   tar czf backup.tar.gz ~/.local/share/containers/storage/volumes/<volume_name>/_data
   ```

2. **Stop existing container**:
   ```bash
   podman stop open-webui  # or your container name
   podman rm open-webui
   ```

3. **Start new container** (with same volume):
   ```bash
   podman run -d \
     --name billable-webui \
     -v webui_data:/app/backend/data \
     -p 3000:8080 \
     billable-open-webui:latest
   ```

4. **Migrations run automatically** - watch the logs to confirm

## Rootless Podman Notes

- **No sudo required** for most operations
- **Volumes stored in**: `~/.local/share/containers/storage/volumes/`
- **Images stored in**: `~/.local/share/containers/storage/`
- **Ports below 1024**: May require special configuration or use ports above 1024

## Verify New Features

1. **Custom Name**: Admin Settings → General → Software Name
2. **Group API Keys**: Admin → Users → Groups → Edit → API Keys tab
3. **Token Usage**: Admin → Users → See "Token Usage (30d)" column

## Troubleshooting

**Container won't start?**
```bash
podman logs billable-webui
```

**Permission issues?**
```bash
# Check if running rootless
podman info | grep rootless

# Check volume permissions
podman volume inspect webui_data
```

**Network issues?**
```bash
# Check podman network
podman network ls
podman network inspect podman
```

**Migrations not running?**
```bash
podman exec -it billable-webui python -c "from open_webui.config import run_migrations; run_migrations()"
```

For detailed documentation, see [PODMAN_BUILD_AND_DEPLOY.md](./PODMAN_BUILD_AND_DEPLOY.md)

