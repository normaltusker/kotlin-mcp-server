# Dockerfile for MCP Kotlin Assistant
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y git curl unzip openjdk-17-jdk nodejs npm bash

# Set working directory
WORKDIR /app

# Install aider
RUN pip install aider-chat python-dotenv

# Install mcp-lsp
RUN npm install -g mcp-lsp

# Expose port for mcp-lsp (default 4000)
EXPOSE 4000

CMD ["/bin/bash"]
