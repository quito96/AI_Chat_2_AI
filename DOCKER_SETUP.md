# 🐳 Docker Setup - AI Multi-Model Discussion System

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)
- `.env` file with API keys in the project directory
- (Optional) `credentials.json` for Google Gemini API

## Quick Start

### 1. Clone project or navigate to project directory

```bash
cd /path/to/AI_Chat_2_AI
```

### 2. Configure environment variables

Create a `.env` file in the project directory:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_CREDENTIALS_PATH=/app/credentials.json
```

### 3. (Optional) Provide Google Credentials

Place your `credentials.json` in the project directory or adjust the path accordingly.

### 4. Start Docker container

```bash
# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 5. Open application

Open your browser and navigate to:
```
http://localhost:8577
```

> **Note:** The port (8577) is configured in `.streamlit/config.toml`

## Management Commands

### Container Management

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs
docker-compose logs -f ai-discussion

# Rebuild containers
docker-compose build --no-cache

# Rebuild and start
docker-compose up -d --build
```

### Debugging

```bash
# Login to container
docker-compose exec ai-discussion /bin/bash

# Python shell in container
docker-compose exec ai-discussion python

# Live container logs
docker-compose logs -f --tail=100 ai-discussion
```

## Configuration

### Environment Variables

The following environment variables can be configured in the `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API Key | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API Key | Yes |
| `GOOGLE_CREDENTIALS_PATH` | Path to Google Credentials JSON | No |

### Streamlit Configuration

The Streamlit configuration is loaded from `.streamlit/config.toml`:

```toml
[server]
port = 8577                    # Application port
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

To change the port, edit `.streamlit/config.toml` and restart the container.

### Volumes

The following directories are mounted from host to container:

- **Code files**: Live-reload for development
- **Assets**: Logo and static files
- **Streamlit config**: `.streamlit/config.toml` for port and theme configuration
- **Database**: `discussions.db` for persistent storage
- **Credentials**: `.env` and `credentials.json` (read-only)

### Ports

- **8577**: Streamlit Web Interface (configured in `.streamlit/config.toml`)

## Production Deployment

For production use:

### 1. Use optimized docker-compose.yml

Create `docker-compose.prod.yml`:

```yaml
services:
  ai-discussion:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-discussion-app
    ports:
      - "8577:8577"
    volumes:
      # Only mount data and credentials
      - ./data:/app/data
      - ./discussions.db:/app/discussions.db
      - ./.streamlit:/app/.streamlit:ro
      - ${GOOGLE_CREDENTIALS_PATH:-./credentials.json}:/app/credentials.json:ro
      - ${ENV_FILE:-.env}:/app/.env:ro

    environment:
      - GOOGLE_CREDENTIALS_PATH=/app/credentials.json
      - PYTHONUNBUFFERED=1

    env_file:
      - .env

    restart: always

    networks:
      - ai-network

networks:
  ai-network:
    driver: bridge
```

### 2. Start production container

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs ai-discussion

# Check container status
docker-compose ps

# Detailed information
docker inspect ai-discussion-app
```

### API keys not recognized

Check:
1. `.env` file exists in project directory
2. Correct syntax in `.env` (no spaces around `=`)
3. Restart container after `.env` changes

```bash
docker-compose down
docker-compose up -d
```

### Google Credentials error

```bash
# Check if credentials.json exists in container
docker-compose exec ai-discussion ls -la /app/credentials.json

# Check if environment variable is set
docker-compose exec ai-discussion env | grep GOOGLE
```

### Port already in use

If port 8577 is already in use:

**Option 1:** Change port in `.streamlit/config.toml`
```toml
[server]
port = 8578
```

Then update `docker-compose.yml`:
```yaml
ports:
  - "8578:8578"
```

**Option 2:** Map to different external port in `docker-compose.yml`
```yaml
ports:
  - "9000:8577"  # Access via http://localhost:9000
```

### Cannot access application

```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs ai-discussion

# Check if port is accessible
curl http://localhost:8577/_stcore/health

# Check firewall settings
# Ensure port 8577 is not blocked by firewall
```

### Memory issues

```bash
# Clean up Docker storage
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Backup & Restore

### Database Backup

```bash
# Create backup
docker-compose exec ai-discussion cp /app/discussions.db /app/data/discussions_backup_$(date +%Y%m%d).db

# Or from host
cp discussions.db discussions_backup_$(date +%Y%m%d).db
```

### Container Image Export

```bash
# Save image
docker save ai_chat_2_ai-ai-discussion:latest | gzip > ai-discussion-image.tar.gz

# Load image
docker load < ai-discussion-image.tar.gz
```

## Development Mode

For active development with live code reloading:

1. Ensure code files are mounted in `docker-compose.yml` (already configured)
2. Start container in development mode:

```bash
docker-compose up
```

3. Edit code on host - changes will be reflected in container
4. Streamlit will auto-reload on file changes

## Security Considerations

### Best Practices

1. **Never commit** `.env` or `credentials.json` to version control
2. Use **read-only** mounts for credentials:
   ```yaml
   volumes:
     - ./credentials.json:/app/credentials.json:ro
   ```
3. Rotate API keys regularly
4. Use environment-specific credentials for production

### File Permissions

Ensure proper file permissions:

```bash
# Restrict .env file
chmod 600 .env

# Restrict credentials
chmod 600 credentials.json
```

## Monitoring

### Container Health

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' ai-discussion-app

# View health check logs
docker inspect --format='{{json .State.Health}}' ai-discussion-app | jq
```

### Resource Usage

```bash
# Monitor resource usage
docker stats ai-discussion-app

# View detailed container info
docker inspect ai-discussion-app
```

## Updating

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Update Dependencies

```bash
# Modify pyproject.toml
# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Additional Information

- **Streamlit Documentation**: https://docs.streamlit.io
- **Docker Documentation**: https://docs.docker.com
- **Project Repository**: https://github.com/quito96/Al_Chat_2_Al

## Support

For issues, please create an issue in the GitHub repository.

---

## Quick Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Shell access
docker-compose exec ai-discussion bash

# Health check
curl http://localhost:8577/_stcore/health
```
