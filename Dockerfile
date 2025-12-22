# =============================================================================
# HTML2PPT Backend Dockerfile
# =============================================================================

# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code
COPY src/ ./src/

# Install the project
RUN uv sync --frozen --no-dev

# =============================================================================
# Stage 2: Production Image
# =============================================================================
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 html2ppt && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home html2ppt

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code
COPY --from=builder /app/src /app/src

# Create data directories
RUN mkdir -p /app/data /app/output && \
    chown -R html2ppt:html2ppt /app

# Switch to non-root user
USER html2ppt

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HTML2PPT_HOST=0.0.0.0 \
    HTML2PPT_PORT=8000 \
    HTML2PPT_DATA_DIR=/app/data \
    HTML2PPT_OUTPUT_DIR=/app/output

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "html2ppt.api.app:app", "--host", "0.0.0.0", "--port", "8000"]