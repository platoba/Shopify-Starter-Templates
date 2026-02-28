FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || pip install --no-cache-dir pytest pytest-cov ruff

# Copy project
COPY . .

# Default: run preview server
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080", "--directory", "minimal-store"]
