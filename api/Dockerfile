FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Sync dependencies using uv
RUN uv sync --frozen --no-dev || uv sync

# Application code will be mounted via volume in compose.yaml

# Expose API port
EXPOSE 8000

# Run the application (overridden by compose.yaml)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
