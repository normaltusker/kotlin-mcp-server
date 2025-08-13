# Dockerfile for Kotlin MCP Server
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    openjdk-17-jdk \
    nodejs \
    npm \
    bash \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt pyproject.toml ./

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make scripts executable
RUN chmod +x kotlin_mcp_server.py && \
    chmod +x servers/mcp-process/mcp-gradle-wrapper.sh 2>/dev/null || true

# Install mcp-lsp (optional for some use cases)
RUN npm install -g mcp-lsp || echo "Note: mcp-lsp installation failed but continuing"

# Create a non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port for MCP server (if running in server mode)
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from kotlin_mcp_server import KotlinMCPServer; print('Health check passed')" || exit 1

# Default command - can be overridden
CMD ["python3", "kotlin_mcp_server.py", "--help"]
