# AI Roadshow — Docker image for lab environments
# This image includes all dependencies pre-installed for offline use.
#
# Quick Start (with persistence):
#   docker run -p 8888:8888 -v $(pwd)/notebooks:/app/notebooks -v $(pwd)/data:/app/data ai-roadshow
#
# Dump your work when done:
#   docker run --rm -v $(pwd)/notebooks:/app/notebooks -v $(pwd)/data:/app/data ai-roadshow dump-work
#
# Air-gapped build (no network during build):
#   docker build -t ai-roadshow . --network=host (or copy vendor/ and data/models/ first)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY notebooks/ /app/notebooks/
COPY pyproject.toml .
COPY data/models/ /app/data/models/

# Vendor arc if present (for air-gapped deployments, pre-stage this)
COPY vendor/ /app/vendor/

# Create .env from example if not present
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Expose Jupyter port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import arcllm, arcrun, arcagent, arcskill; print('OK')" || exit 1

# Create output directory for work dump
RUN mkdir -p /app/output

# Entry point script handles multiple modes
COPY scripts/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]