FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

# Expose the port that Azure expects
EXPOSE 8000

# Set environment variables
ENV PORT=8000

# Run the application
CMD ["./startup.sh"] 