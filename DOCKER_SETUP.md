# Docker Setup Guide for Kotlin MCP Server

## 📋 Prerequisites

### Install Docker

#### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download from: https://docs.docker.com/desktop/mac/install/
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
sudo yum install docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

## 🚀 Quick Start

### 1. Build the Docker Image
```bash
# Using the setup script (recommended)
./docker-setup.sh build

# Or manually
docker build -t kotlin-mcp-server .
```

### 2. Run Interactive Container
```bash
# Start interactive container for development
./docker-setup.sh start

# Or manually
docker-compose up -d kotlin-mcp-server
docker exec -it kotlin-mcp-server bash
```

### 3. Run as Daemon (Production)
```bash
# Start MCP server in daemon mode
./docker-setup.sh daemon /path/to/your/android/project

# Or manually
ANDROID_PROJECT_PATH=/path/to/project docker-compose --profile daemon up -d
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Project configuration
ANDROID_PROJECT_PATH=/path/to/your/android/project
MCP_SERVER_NAME=kotlin-android
PROJECT_PATH=/workspace

# Optional: AI integration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional: Security
ENCRYPTION_KEY=your_encryption_key
LOG_LEVEL=INFO
```

### Volume Mounts

The Docker setup includes several volume mounts:

- **Project Code**: `.:/app` - Mounts the MCP server code
- **Android Project**: `${ANDROID_PROJECT_PATH}:/workspace` - Your Android project
- **Configuration**: Automatically handled by environment variables

## 📝 Available Commands

### Using docker-setup.sh Script

```bash
# Build the image
./docker-setup.sh build

# Start interactive container
./docker-setup.sh start

# Start daemon mode
./docker-setup.sh daemon [android-project-path]

# Stop containers
./docker-setup.sh stop

# View logs
./docker-setup.sh logs [service-name]

# Open shell
./docker-setup.sh shell

# Run tests
./docker-setup.sh test

# Clean up
./docker-setup.sh clean
```

### Manual Docker Commands

```bash
# Build image
docker build -t kotlin-mcp-server .

# Run with volume mounts
docker run -it --rm \
  -v $(pwd):/app \
  -v /path/to/android/project:/workspace \
  -p 4000:4000 \
  kotlin-mcp-server

# Run specific command
docker run --rm \
  -v $(pwd):/app \
  -v /path/to/android/project:/workspace \
  kotlin-mcp-server \
  python3 kotlin_mcp_server.py /workspace
```

## 🐳 Docker Compose Services

### kotlin-mcp-server (Interactive)
- **Purpose**: Development and interactive use
- **Ports**: 4000:4000, 8080:8080
- **Command**: Interactive bash shell
- **Usage**: `docker-compose up -d kotlin-mcp-server`

### kotlin-mcp-server-daemon (Production)
- **Purpose**: Run MCP server as a service
- **Ports**: 4001:4000
- **Command**: Runs the MCP server directly
- **Usage**: `docker-compose --profile daemon up -d`

## 🔍 Health Checks

The Docker setup includes health checks to ensure the server is running correctly:

```bash
# Check container health
docker ps

# View health check logs
docker inspect kotlin-mcp-server | grep -A 5 Health

# Manual health check
docker exec kotlin-mcp-server python3 -c "from kotlin_mcp_server import KotlinMCPServer; print('OK')"
```

## 🛠️ Development Workflow

### 1. Development Setup
```bash
# Start development container
./docker-setup.sh start

# Open shell
./docker-setup.sh shell

# Inside container - run tests
python3 -m pytest test_*.py -v

# Install additional packages
pip install package-name
```

### 2. Testing in Docker
```bash
# Run all tests
./docker-setup.sh test

# Run specific test file
docker exec kotlin-mcp-server python3 -m pytest test_kotlin_mcp_server.py -v

# Run with coverage
docker exec kotlin-mcp-server python3 -m pytest --cov=. --cov-report=html
```

### 3. Debugging
```bash
# View container logs
./docker-setup.sh logs kotlin-mcp-server

# View MCP server logs
docker exec kotlin-mcp-server tail -f mcp_security.log

# Interactive debugging
docker exec -it kotlin-mcp-server python3 -c "
import kotlin_mcp_server
server = kotlin_mcp_server.KotlinMCPServer('debug')
print(f'Server: {server.name}')
"
```

## 📊 Production Deployment

### Using Docker Compose (Recommended)
```bash
# Create production environment
cp docker-compose.yml docker-compose.prod.yml

# Edit production settings
# - Remove development volume mounts
# - Set proper environment variables
# - Configure resource limits

# Deploy
docker-compose -f docker-compose.prod.yml up -d kotlin-mcp-server-daemon
```

### Resource Limits
```yaml
# Add to docker-compose.yml
services:
  kotlin-mcp-server-daemon:
    # ... existing config
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🔒 Security Considerations

### Non-Root User
The Dockerfile creates and uses a non-root user (`mcpuser`) for security.

### File Permissions
```bash
# Check permissions in container
docker exec kotlin-mcp-server ls -la /app

# Fix permissions if needed
docker exec kotlin-mcp-server chown -R mcpuser:mcpuser /app
```

### Network Security
```yaml
# Custom network in docker-compose.yml
networks:
  mcp-network:
    driver: bridge

services:
  kotlin-mcp-server:
    networks:
      - mcp-network
```

## 🐛 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Clear Docker cache and rebuild
docker system prune -a
./docker-setup.sh build

# Check build logs
docker build --no-cache -t kotlin-mcp-server .
```

#### Permission Issues
```bash
# Fix volume mount permissions
docker exec -it kotlin-mcp-server bash
chown -R mcpuser:mcpuser /app /workspace
```

#### Container Won't Start
```bash
# Check logs
./docker-setup.sh logs kotlin-mcp-server

# Run with different command
docker run -it --rm kotlin-mcp-server bash
```

#### Python Import Errors
```bash
# Check Python path
docker exec kotlin-mcp-server python3 -c "import sys; print(sys.path)"

# Reinstall dependencies
docker exec kotlin-mcp-server pip install -r requirements.txt
```

### Performance Issues
```bash
# Monitor resource usage
docker stats kotlin-mcp-server

# Check container processes
docker exec kotlin-mcp-server ps aux

# Adjust memory limits in docker-compose.yml
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Python Docker Images](https://pythonspeed.com/docker/)
- [MCP Server Documentation](../README.md)
