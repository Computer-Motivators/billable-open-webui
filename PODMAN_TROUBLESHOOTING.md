# Podman Troubleshooting Guide

Common issues and solutions when deploying the customized Open WebUI with Podman.

## Database Connection Issues

### Issue: "Unrecognized or unsupported scheme: ''"

**Symptoms:**
```
Failed to initialize the database connection: Unrecognized or unsupported scheme: "".
```

**Cause:** The `DATABASE_URL` environment variable has a leading dash or is malformed.

**Solution:**
```bash
# ❌ WRONG - has leading dash in the value
podman run -e DATABASE_URL="-sqlite:///./data/webui.db" ...

# ✅ CORRECT - no leading dash
podman run -e DATABASE_URL="sqlite:///./data/webui.db" ...

# Or omit DATABASE_URL to use default SQLite location
podman run ... billable-open-webui:latest
```

**Explanation:** The `-e` flag is the dash for setting environment variables. The value itself should not start with a dash.

### Issue: "UnboundLocalError: cannot access local variable 'db'"

**Symptoms:**
```
UnboundLocalError: cannot access local variable 'db' where it is not associated with a value
```

**Cause:** This was a bug in error handling that has been fixed. If you see this, ensure you're using the latest build.

**Solution:** Rebuild the image with the latest code:
```bash
podman build -t billable-open-webui:latest .
```

### Issue: Database file not found or permission denied

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solution:**
```bash
# Check volume mount
podman volume inspect webui_data

# Verify volume permissions (rootless)
ls -la ~/.local/share/containers/storage/volumes/

# Fix permissions if needed
podman unshare chown -R $(id -u):$(id -g) ~/.local/share/containers/storage/volumes/webui_data/_data
```

## Container Startup Issues

### Issue: Container exits immediately

**Diagnosis:**
```bash
# Check logs
podman logs billable-open-webui

# Check exit code
podman inspect billable-open-webui | grep -i exitcode
```

**Common Causes:**

1. **Database connection failure**
   - Check `DATABASE_URL` is correct
   - Verify database file/volume exists
   - Check permissions

2. **Missing environment variables**
   - Ensure `WEBUI_SECRET_KEY` is set (or let it auto-generate)
   - Verify `OLLAMA_BASE_URL` if using Ollama

3. **Port conflicts**
   ```bash
   # Check if port is in use
   sudo netstat -tulpn | grep 3200
   # Or use different port
   podman run -p 3201:8080 ...
   ```

### Issue: Container won't start (rootless)

**Symptoms:**
```
Error: cannot connect to Podman. Please verify your connection to the Podman socket
```

**Solution:**
```bash
# Start podman machine (macOS/Windows)
podman machine start

# Check podman socket
podman info

# Verify rootless mode
podman info | grep rootless
```

## Network Issues

### Issue: Containers can't communicate

**Symptoms:**
- Open WebUI can't connect to Ollama
- Database connection fails

**Solution:**
```bash
# Check network
podman network ls

# Inspect network
podman network inspect podman

# Use podman-compose for automatic networking
podman-compose up -d
```

### Issue: Can't access from host

**Symptoms:**
- Can't access http://localhost:3200

**Solution:**
```bash
# Check port binding
podman port billable-open-webui

# Verify container is running
podman ps

# Check firewall
sudo firewall-cmd --list-ports  # Fedora/RHEL
sudo ufw status  # Ubuntu/Debian
```

## Volume Issues

### Issue: Data not persisting

**Symptoms:**
- Settings reset after container restart
- Database appears empty

**Solution:**
```bash
# Verify volume is mounted
podman inspect billable-open-webui | grep -A 10 Mounts

# Check volume exists
podman volume ls

# Create volume if missing
podman volume create webui_data
```

### Issue: Permission denied on volumes (rootless)

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/app/backend/data'
```

**Solution:**
```bash
# Check volume location
podman volume inspect webui_data

# Fix permissions
podman unshare chown -R $(id -u):$(id -g) \
  ~/.local/share/containers/storage/volumes/webui_data/_data
```

## Migration Issues

### Issue: Migrations not running

**Symptoms:**
- `token_usage` table missing
- Errors about missing columns

**Solution:**
```bash
# Check migration logs
podman logs billable-open-webui | grep -i migration

# Manually run migrations
podman exec -it billable-open-webui bash
cd /app/backend
alembic upgrade head
```

### Issue: Migration conflicts

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision identified by '...'
```

**Solution:**
```bash
# Check current migration version
podman exec -it billable-open-webui alembic current

# View migration history
podman exec -it billable-open-webui alembic history

# Force to specific revision if needed (use with caution)
podman exec -it billable-open-webui alembic stamp head
```

## SELinux Issues (Fedora/RHEL)

### Issue: SELinux blocking access

**Symptoms:**
```
Permission denied errors
SELinux audit logs show denials
```

**Solution:**
```bash
# Check SELinux status
getenforce

# View recent denials
sudo ausearch -m avc -ts recent

# Temporarily set permissive (for testing)
sudo setenforce 0

# Or configure proper SELinux policies
sudo setsebool -P container_manage_cgroup on
```

## Build Issues

### Issue: Build fails with "out of memory"

**Solution:**
```bash
# Increase available memory or use build cache
podman build --memory=8g -t billable-open-webui:latest .

# Or build in stages
podman build --target build -t billable-open-webui:build .
podman build --target base -t billable-open-webui:latest .
```

### Issue: Can't pull base images

**Solution:**
```bash
# Configure registries
# Edit ~/.config/containers/registries.conf

# Or use --registry flag
podman build --registry docker.io ...
```

## Quick Diagnostic Commands

```bash
# Check container status
podman ps -a

# View all logs
podman logs billable-open-webui

# View recent logs (last 100 lines)
podman logs --tail 100 billable-open-webui

# Follow logs in real-time
podman logs -f billable-open-webui

# Check container resource usage
podman stats billable-open-webui

# Inspect container configuration
podman inspect billable-open-webui

# Check environment variables
podman exec billable-open-webui env | grep -E "DATABASE|WEBUI|OLLAMA"

# Test database connection
podman exec billable-open-webui python -c "
from open_webui.env import DATABASE_URL
print(f'Database URL: {DATABASE_URL}')
"

# Check if migrations ran
podman exec billable-open-webui python -c "
from open_webui.internal.db import get_db
from sqlalchemy import inspect
with get_db() as db:
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    print('Tables:', tables)
    if 'token_usage' in tables:
        print('✓ token_usage table exists')
"
```

## Getting Help

If issues persist:

1. **Collect diagnostic information:**
   ```bash
   # Save logs
   podman logs billable-open-webui > webui_logs.txt
   
   # Save container info
   podman inspect billable-open-webui > container_info.json
   
   # Save podman info
   podman info > podman_info.txt
   ```

2. **Check the main documentation:**
   - [PODMAN_BUILD_AND_DEPLOY.md](./PODMAN_BUILD_AND_DEPLOY.md)
   - [PODMAN_QUICK_START.md](./PODMAN_QUICK_START.md)

3. **Verify your setup:**
   - Podman version is up to date
   - All prerequisites are installed
   - Environment variables are set correctly
   - Volumes are properly configured

