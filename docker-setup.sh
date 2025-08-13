#!/bin/bash
# Docker setup script for Kotlin MCP Server
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Kotlin MCP Server Docker Setup${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Determine which docker compose command to use
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

print_info "Using: $COMPOSE_CMD"

# Parse command line arguments
COMMAND=${1:-"help"}

case $COMMAND in
    "build")
        print_info "Building Kotlin MCP Server Docker image..."
        $COMPOSE_CMD build kotlin-mcp-server
        print_status "Docker image built successfully!"
        ;;
    
    "start")
        print_info "Starting Kotlin MCP Server container..."
        $COMPOSE_CMD up -d kotlin-mcp-server
        print_status "Container started! Access with: docker exec -it kotlin-mcp-server bash"
        ;;
    
    "daemon")
        print_info "Starting MCP Server in daemon mode..."
        ANDROID_PROJECT_PATH=${2:-"./sample-project"}
        export ANDROID_PROJECT_PATH
        $COMPOSE_CMD --profile daemon up -d kotlin-mcp-server-daemon
        print_status "MCP Server daemon started on port 4001"
        ;;
    
    "stop")
        print_info "Stopping all containers..."
        $COMPOSE_CMD down
        print_status "Containers stopped"
        ;;
    
    "logs")
        SERVICE=${2:-"kotlin-mcp-server"}
        print_info "Showing logs for $SERVICE..."
        $COMPOSE_CMD logs -f $SERVICE
        ;;
    
    "shell")
        print_info "Opening shell in container..."
        docker exec -it kotlin-mcp-server bash
        ;;
    
    "test")
        print_info "Running tests in container..."
        docker exec -it kotlin-mcp-server python3 -m pytest test_*.py -v
        ;;
    
    "clean")
        print_info "Cleaning up Docker resources..."
        $COMPOSE_CMD down --rmi local --volumes --remove-orphans
        print_status "Cleanup complete"
        ;;
    
    "help"|*)
        echo -e "${BLUE}Kotlin MCP Server Docker Commands:${NC}"
        echo ""
        echo "  build              Build the Docker image"
        echo "  start              Start the interactive container"
        echo "  daemon [path]      Start MCP server in daemon mode"
        echo "  stop               Stop all containers"
        echo "  logs [service]     Show container logs"
        echo "  shell              Open bash shell in container"
        echo "  test               Run tests in container"
        echo "  clean              Remove containers and images"
        echo "  help               Show this help message"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo "  ./docker-setup.sh build"
        echo "  ./docker-setup.sh start"
        echo "  ./docker-setup.sh daemon /path/to/android/project"
        echo "  ./docker-setup.sh logs kotlin-mcp-server"
        echo ""
        ;;
esac
