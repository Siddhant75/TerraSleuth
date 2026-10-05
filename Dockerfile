# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8501

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY .streamlit/ /app/.streamlit/

# Pre-seed cache database for instant zero-credit demo
RUN python -c "from backend.app.services.cache_service import seed_golden_cases; seed_golden_cases()"

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Entrypoint to run Streamlit app
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
