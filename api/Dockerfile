FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Install dependencies using pip
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Expose API port
EXPOSE 8000

# Run the application (overridden by compose.yaml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
