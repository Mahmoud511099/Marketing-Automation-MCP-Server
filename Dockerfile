FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages for demo
RUN pip install --no-cache-dir \
    jupyter \
    notebook \
    plotly \
    kaleido \
    psycopg2-binary \
    redis \
    flask \
    gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/reports /app/logs /app/output

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
CMD ["python", "-m", "src.server"]