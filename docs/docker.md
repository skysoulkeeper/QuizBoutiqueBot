# Docker Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Configuration Priority](#configuration-priority)
- [Docker Setup](#docker-setup)
  - [Using Docker Compose](#using-docker-compose)
  - [Using Docker CLI](#using-docker-cli)
- [Volume Management](#volume-management)
- [Networking](#networking)
- [Health Checks](#health-checks)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Production Best Practices](#production-best-practices)

## Overview

QuizBoutiqueBot uses a **hybrid configuration approach** combining YAML configuration files with environment variable overrides. This provides flexibility for both local development and containerized deployments while maintaining security best practices.

### Key Features
- ✅ Multi-stage Docker build for optimized image size
- ✅ Non-root user execution for enhanced security
- ✅ Named volumes for data persistence
- ✅ Health check monitoring
- ✅ Environment-based configuration overrides
- ✅ Resource limits and constraints

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Container Startup Flow                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. docker-compose.yml reads .env file                       │
│     ↓                                                         │
│  2. ENV variables injected into container                    │
│     ↓                                                         │
│  3. entrypoint.py executes                                   │
│     ├─ Reads configs/config.yml (base configuration)         │
│     ├─ Merges with ENV variables                             │
│     └─ Generates configs/config.dev.yml (runtime config)     │
│     ↓                                                         │
│  4. app.py starts                                             │
│     └─ ConfigLoader reads config.dev.yml (if exists)         │
│        or falls back to config.yml                           │
│     ↓                                                         │
│  5. Bot starts polling Telegram API                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Pre-built Images

QuizBoutiqueBot provides pre-built multi-platform Docker images via GitHub Container Registry.

### Supported Platforms
- **linux/amd64** - Intel/AMD processors (standard PCs, servers, NAS)
- **linux/arm64** - ARM processors (Apple Silicon M1/M2/M3, Raspberry Pi 4/5)

### Pull from GHCR
```bash
# Pull latest stable version
docker pull ghcr.io/skysoulkeeper/quizboutiquebot:latest

# Run without building
docker compose up -d
```

The `docker-compose.yml` already uses the pre-built image from GHCR, so you don't need to build locally for production deployments.

### Building Multi-Platform Images

For contributors and developers who want to build and push multi-platform images:
```bash
# First time setup (run once)
make setup-builder

# Login to GHCR
make login

# Build and push multi-platform image
make build-push
```

See [Makefile](../Makefile) for available build targets.

### 1. Clone Repository
```bash
git clone https://github.com/skysoulkeeper/QuizBoutiqueBot.git
cd QuizBoutiqueBot
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your bot token
nano .env
```

**Minimum required configuration:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Launch
```bash
# Build and start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Configuration

### Environment Variables

QuizBoutiqueBot supports configuration via environment variables for deployment-specific settings while keeping structural configuration in YAML files.

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | `123456789:ABC-DEF...` |

#### Optional Variables

**General Settings:**
| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_CHAT_ID` | - | Specific chat ID for notifications |
| `QBB_ENV` | `prod` | Environment mode (`dev`/`prod`) |
| `QBB_LANGUAGE` | `en` | Bot interface language (`en`/`es`/`ru`/`ua`) |
| `QBB_PARSE_MODE` | `HTML` | Telegram message parse mode (`HTML`/`Markdown`) |

**Logging:**
| Variable | Default | Description |
|----------|---------|-------------|
| `QBB_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`/`INFO`/`WARNING`/`ERROR`) |
| `QBB_LOG_TO_FILE` | `false` | Enable file logging |

**Proxy Settings:**
| Variable | Default | Description |
|----------|---------|-------------|
| `QBB_PROXY_ENABLED` | `false` | Enable proxy usage |
| `QBB_PROXY_HOST` | - | Proxy server hostname/IP |
| `QBB_PROXY_PORT` | `1080` | Proxy server port |
| `QBB_PROXY_PROTOCOL` | `socks` | Proxy protocol (`http`/`https`/`socks`) |
| `QBB_PROXY_USERNAME` | - | Proxy authentication username |
| `QBB_PROXY_PASSWORD` | - | Proxy authentication password |

### Configuration Priority

Configuration values are resolved in the following order (highest to lowest):

1. **Environment Variables** (highest priority)
2. **config.dev.yml** (generated at runtime from ENV)
3. **config.yml** (base configuration)

Example:
```yaml
# config.yml (base)
telegram:
  token: ""
  language: "en"

# ENV variable
QBB_LANGUAGE=ru

# Result: language will be "ru"
```

## Docker Setup

### Using Docker Compose

#### Development Mode
```bash
# Use development compose file with hot-reload
docker compose -f docker-compose.dev.yml up
```

#### Production Mode
```bash
# Build with specific tag
docker compose build

# Start services
docker compose up -d

# View service status
docker compose ps

# Follow logs
docker compose logs -f quizboutiquebot

# Restart service
docker compose restart quizboutiquebot

# Stop and remove containers
docker compose down

# Stop and remove volumes (⚠️ deletes data!)
docker compose down -v
```

### Using Docker CLI

If you prefer not to use Docker Compose:

```bash
# Build image
docker build -t qbb:latest .

# Run container
docker run -d \
  --name quizboutiquebot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="your_token_here" \
  -e QBB_LANGUAGE=en \
  -e QBB_LOG_LEVEL=INFO \
  -v qbb-logs:/app/data/logs \
  -v qbb-db:/app/data/db \
  qbb:latest

# View logs
docker logs -f quizboutiquebot

# Stop container
docker stop quizboutiquebot

# Remove container
docker rm quizboutiquebot
```

## Volume Management

### Named Volumes

The bot uses named volumes for persistent data:

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `logs-data` | `/app/data/logs` | Application logs |
| `db-data` | `/app/data/db` | User data and quiz progress |

### Backup Volumes

```bash
# Backup logs volume
docker run --rm \
  -v logs-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz /data

# Backup database volume
docker run --rm \
  -v db-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db-backup.tar.gz /data
```

### Restore Volumes

```bash
# Restore logs
docker run --rm \
  -v logs-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/logs-backup.tar.gz -C /

# Restore database
docker run --rm \
  -v db-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/db-backup.tar.gz -C /
```

### Custom Question Pools

To use custom question pools, uncomment the volume mount in `docker-compose.yml`:

```yaml
volumes:
  # Mount custom questions (read-only)
  - ./data/questions:/app/data/questions:ro
```

Then place your JSON quiz files in `./data/questions/<category>/`.

## Networking

### Default Network

The bot runs on Docker's default bridge network and requires outbound internet access to communicate with Telegram's API.

### Proxy Support

For environments requiring proxy access:

```bash
# In .env file
QBB_PROXY_ENABLED=true
QBB_PROXY_HOST=proxy.example.com
QBB_PROXY_PORT=1080
QBB_PROXY_PROTOCOL=socks
QBB_PROXY_USERNAME=user
QBB_PROXY_PASSWORD=pass
```

### Firewall Requirements

**Outbound (required):**
- TCP 443 (HTTPS) to `api.telegram.org`
- Your proxy server (if configured)

**Inbound:** None required (bot uses polling, not webhooks)

## Health Checks

### Built-in Health Check

The container includes a health check that monitors the Python process:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*app.py" || exit 1
```

### Monitor Health Status

```bash
# Check container health
docker compose ps

# View health check logs
docker inspect quizboutiquebot --format='{{json .State.Health}}' | jq

# Continuous monitoring
watch -n 5 'docker compose ps'
```

### Health Check Behavior

- **Interval:** Checks every 30 seconds
- **Timeout:** 10 seconds per check
- **Start Period:** 10 second grace period on startup
- **Retries:** 3 failed checks before marking unhealthy
- **Auto-restart:** Container restarts if unhealthy (when using `restart: unless-stopped`)

## Security

### Security Features

1. **Non-root User Execution**
   - Container runs as user `qbb` (UID 10001)
   - No privileged access required

2. **No New Privileges**
   ```yaml
   security_opt:
     - no-new-privileges:true
   ```

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
   ```

4. **Secrets Management**
   - Sensitive data via environment variables
   - `.env` file excluded from git
   - No secrets in image layers

## Troubleshooting

### Common Issues

#### 1. Bot Won't Start - Missing Token

**Symptom:**
```
ERROR: TELEGRAM_BOT_TOKEN is required!
```

**Solution:**
```bash
# Check .env file exists and contains token
cat .env | grep TELEGRAM_BOT_TOKEN

# Recreate from example
cp .env.example .env
nano .env
```

#### 2. Module Not Found Error

**Symptom:**
```
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
```bash
# Rebuild without cache
docker compose build --no-cache
docker compose up -d
```

#### 3. Container Keeps Restarting

**Symptom:**
```bash
docker compose ps
# Shows container restarting repeatedly
```

**Solution:**
```bash
# Check logs for errors
docker compose logs quizboutiquebot

# Common causes:
# - Invalid bot token
# - Network connectivity issues
# - Missing required files
```

#### 4. Permission Denied Errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/app/data/logs/...'
```

**Solution:**
```bash
# Fix volume permissions
docker compose down
docker volume rm logs-data db-data
docker compose up -d --build
```

#### 5. Config Not Updating

**Symptom:**
Environment variable changes not reflected in bot behavior.

**Solution:**
```bash
# Recreate container to pick up new ENV
docker compose up -d --force-recreate

# Verify ENV variables in container
docker compose exec quizboutiquebot env | grep QBB_
```

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
# In .env
QBB_LOG_LEVEL=DEBUG
QBB_LOG_TO_FILE=true

# Restart and check logs
docker compose restart
docker compose logs -f
```

### Access Container Shell

```bash
# Execute bash in running container
docker compose exec quizboutiquebot bash

# Check configuration
cat /app/configs/config.dev.yml

# Check Python packages
pip list

# Exit shell
exit
```

## Documentation
- [Main README](../README.md) - General project documentation
- [Database Guide](docs/database.md)
- [Telegram Bot API](https://core.telegram.org/bots/api) - Official API documentation
- [Docker Documentation](https://docs.docker.com/) - Docker reference
