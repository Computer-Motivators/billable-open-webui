# Deployment Checklist

Use this checklist when deploying the customized Open WebUI build to ensure a smooth deployment.

## Pre-Deployment

- [ ] **Backup existing data** (if upgrading)
  ```bash
  docker run --rm -v <volume_name>:/data -v $(pwd):/backup \
    alpine tar czf /backup/webui_backup_$(date +%Y%m%d).tar.gz -C /data .
  ```

- [ ] **Review environment variables**
  - [ ] `WEBUI_SECRET_KEY` is set and secure
  - [ ] `DATABASE_URL` is correct
  - [ ] `OLLAMA_BASE_URL` points to correct Ollama instance
  - [ ] `WEBUI_NAME_CUSTOM` is set (optional)

- [ ] **Verify Docker resources**
  - [ ] Sufficient disk space (10GB+)
  - [ ] Sufficient RAM (4GB+)
  - [ ] Docker and Docker Compose are up to date

- [ ] **Test build locally**
  ```bash
  docker build -t billable-open-webui:test .
  ```

## Deployment Steps

- [ ] **Stop existing services** (if upgrading)
  ```bash
  docker compose down
  ```

- [ ] **Update docker-compose.yaml**
  - [ ] Image/build context points to new build
  - [ ] Volume mounts are preserved
  - [ ] Environment variables are updated

- [ ] **Start services**
  ```bash
  docker compose up -d
  ```

- [ ] **Monitor startup logs**
  ```bash
  docker compose logs -f open-webui
  ```

- [ ] **Verify migrations ran**
  - [ ] Check logs for "Running migrations"
  - [ ] No migration errors in logs
  - [ ] `token_usage` table exists (if using PostgreSQL/SQLite CLI)

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

## Rollback Plan

If issues occur:

- [ ] **Stop new container**
  ```bash
  docker compose down
  ```

- [ ] **Restore previous image/configuration**
  - [ ] Revert docker-compose.yaml
  - [ ] Restore from backup if needed

- [ ] **Verify rollback**
  - [ ] Service starts successfully
  - [ ] Data is intact
  - [ ] Users can access system

## Monitoring

- [ ] **Set up log monitoring**
  ```bash
  docker compose logs -f --tail=100 open-webui
  ```

- [ ] **Monitor resource usage**
  ```bash
  docker stats billable-open-webui
  ```

- [ ] **Check database size** (if using SQLite)
  ```bash
  docker exec billable-open-webui \
    du -h /app/backend/data/webui.db
  ```

## Documentation

- [ ] **Update deployment documentation** with:
  - [ ] Build date/version
  - [ ] Configuration changes
  - [ ] Known issues or workarounds

- [ ] **Document custom configurations**
  - [ ] Software name setting
  - [ ] Group API key configurations
  - [ ] Token usage tracking setup

