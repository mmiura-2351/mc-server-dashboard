FROM python:3.13-slim

WORKDIR /app

# Install essential packages only (minimal for development)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    httpx \
    pytest \
    pytest-asyncio || true

# Application code will be mounted via volume in compose.yaml

# Expose API port
EXPOSE 8000

# Run the application (overridden by compose.yaml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
