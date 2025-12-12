# Podman Deployment Checklist

Use this checklist when deploying the customized Open WebUI Podman build to ensure a smooth deployment.

## Pre-Deployment

- [ ] **Install Podman**
  ```bash
  # Fedora/RHEL
  sudo dnf install podman podman-compose
  
  # Ubuntu/Debian
  sudo apt-get install podman podman-compose
  
  # Verify installation
  podman --version
  ```

- [ ] **Verify Podman is working**
  ```bash
  podman info
  podman run hello-world
  ```

- [ ] **Backup existing data** (if upgrading)
  ```bash
  # Find volume location
  podman volume inspect <volume_name>
  
  # Backup volume data
  tar czf webui_backup_$(date +%Y%m%d).tar.gz \
    ~/.local/share/containers/storage/volumes/<volume_name>/_data
  ```

- [ ] **Review environment variables**
  - [ ] `WEBUI_SECRET_KEY` is set and secure
  - [ ] `DATABASE_URL` is correct
  - [ ] `OLLAMA_BASE_URL` points to correct Ollama instance
  - [ ] `WEBUI_NAME_CUSTOM` is set (optional)

- [ ] **Verify Podman resources**
  - [ ] Sufficient disk space (10GB+)
  - [ ] Sufficient RAM (4GB+)
  - [ ] Podman is up to date

- [ ] **Test build locally**
  ```bash
  podman build -t billable-open-webui:test .
  ```

- [ ] **Check rootless configuration** (if running rootless)
  ```bash
  podman info | grep rootless
  # Should show: rootless: true
  ```

## Deployment Steps

- [ ] **Stop existing services** (if upgrading)
  ```bash
  podman stop open-webui  # or container name
  podman rm open-webui
  # Or with podman-compose:
  podman-compose down
  ```

- [ ] **Update podman-compose.yaml**
  - [ ] Image/build context points to new build
  - [ ] Volume mounts are preserved
  - [ ] Environment variables are updated

- [ ] **Start services**
  ```bash
  podman-compose up -d
  # Or rebuild:
  podman-compose up -d --build
  ```

- [ ] **Monitor startup logs**
  ```bash
  podman-compose logs -f open-webui
  # Or:
  podman logs -f billable-open-webui
  ```

- [ ] **Verify migrations ran**
  - [ ] Check logs for "Running migrations"
  - [ ] No migration errors in logs
  - [ ] `token_usage` table exists

## Post-Deployment Verification

- [ ] **Health check passes**
  ```bash
  curl http://localhost:3000/health
  ```

- [ ] **Can access web UI**
  - [ ] Login page loads
  - [ ] Can log in with admin credentials

- [ ] **New features work**
  - [ ] Custom software name can be set in admin settings
  - [ ] Group API keys tab appears in group editing
  - [ ] Token usage column appears in users list

- [ ] **Database integrity**
  - [ ] Existing users can log in
  - [ ] Existing chats are accessible
  - [ ] Groups and permissions are intact

- [ ] **API endpoints respond**
  ```bash
  # Test token usage endpoint
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:3000/api/users/admin/users/token-usage
  ```

- [ ] **Volume persistence**
  ```bash
  # Verify volumes exist
  podman volume ls
  
  # Check volume location
  podman volume inspect webui_data
  ```

## Rootless-Specific Checks

- [ ] **Verify running rootless**
  ```bash
  podman info | grep rootless
  ```

- [ ] **Check volume permissions**
  ```bash
  ls -la ~/.local/share/containers/storage/volumes/
  ```

- [ ] **Verify port binding** (if using ports < 1024)
  ```bash
  # Check if unprivileged ports are configured
  sysctl net.ipv4.ip_unprivileged_port_start
  ```

- [ ] **Check SELinux** (if on Fedora/RHEL)
  ```bash
  getenforce
  # If enforcing, check for SELinux denials:
  sudo ausearch -m avc -ts recent
  ```

## Rollback Plan

If issues occur:

- [ ] **Stop new container**
  ```bash
  podman-compose down
  # Or:
  podman stop billable-open-webui
  podman rm billable-open-webui
  ```

- [ ] **Restore previous image/configuration**
  - [ ] Revert podman-compose.yaml
  - [ ] Restore from backup if needed

- [ ] **Verify rollback**
  - [ ] Service starts successfully
  - [ ] Data is intact
  - [ ] Users can access system

## Monitoring

- [ ] **Set up log monitoring**
  ```bash
  podman-compose logs -f --tail=100 open-webui
  # Or:
  podman logs -f billable-open-webui
  ```

- [ ] **Monitor resource usage**
  ```bash
  podman stats billable-open-webui
  ```

- [ ] **Check container health**
  ```bash
  podman ps
  podman inspect billable-open-webui | grep -i health
  ```

- [ ] **Check database size** (if using SQLite)
  ```bash
  podman exec billable-open-webui \
    du -h /app/backend/data/webui.db
  ```

## Podman-Specific Considerations

- [ ] **Network connectivity**
  ```bash
  # Verify containers can communicate
  podman network ls
  podman network inspect podman
  ```

- [ ] **Volume management**
  ```bash
  # List volumes
  podman volume ls
  
  # Inspect volume details
  podman volume inspect webui_data
  ```

- [ ] **Image management**
  ```bash
  # List images
  podman images
  
  # Clean up unused images
  podman image prune
  ```

## Documentation

- [ ] **Update deployment documentation** with:
  - [ ] Build date/version
  - [ ] Configuration changes
  - [ ] Known issues or workarounds
  - [ ] Podman-specific notes

- [ ] **Document custom configurations**
  - [ ] Software name setting
  - [ ] Group API key configurations
  - [ ] Token usage tracking setup
  - [ ] Rootless configuration (if applicable)

## Troubleshooting Quick Reference

**Container exits immediately?**
```bash
podman logs billable-open-webui
```

**Permission denied errors?**
```bash
# Check if running rootless
podman info | grep rootless

# Check volume permissions
podman volume inspect webui_data
```

**Network issues?**
```bash
podman network ls
podman network inspect podman
```

**SELinux blocking?**
```bash
sudo ausearch -m avc -ts recent
sudo setenforce 0  # Temporarily for testing
```

For detailed troubleshooting, see [PODMAN_BUILD_AND_DEPLOY.md](./PODMAN_BUILD_AND_DEPLOY.md)

