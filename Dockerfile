# syntax=docker/dockerfile:1.7
# QuizBoutiqueBot Dockerfile (Python 3.11)

# Build stage - for future use if needed (e.g., compiling deps)
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim AS runtime

# Security and performance env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random

# Install runtime dependencies only
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user FIRST
RUN useradd -m -u 10001 -s /bin/bash qbb

WORKDIR /app

# Copy Python packages from builder to qbb's home
COPY --from=builder --chown=qbb:qbb /root/.local /home/qbb/.local

# Copy application code
COPY --chown=qbb:qbb . /app

# Create necessary directories with proper permissions
RUN mkdir -p \
    /app/data/logs \
    /app/data/db \
    /app/data/questions \
    /app/data/recognition \
    /app/data/user_data \
    && chown -R qbb:qbb /app/data \
    && chmod -R 755 /app/data

# Switch to non-root user
USER qbb

# Set PATH for qbb user
ENV PATH=/home/qbb/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD pgrep -f "python.*app.py" || exit 1

ENTRYPOINT ["python", "/app/docker/entrypoint.py"]
