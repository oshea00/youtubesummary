FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY mcp_wrapper.py .

# Make the wrapper executable
RUN chmod +x mcp_wrapper.py

# Create a non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Set Python path to include src directory
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Expose the MCP wrapper as the entrypoint
ENTRYPOINT ["python", "mcp_wrapper.py"]