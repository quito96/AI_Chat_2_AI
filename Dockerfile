# Dockerfile für AI Multi-Model Discussion System
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies, License und README
COPY pyproject.toml License README.md ./

# uv installieren für schnellere Dependency-Installation
RUN pip install --no-cache-dir uv

# Dependencies installieren
RUN uv pip install --system --no-cache -e .

# Anwendungscode kopieren
COPY . .

# Streamlit Port (configured in .streamlit/config.toml)
EXPOSE 8577

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8577/_stcore/health || exit 1

# Streamlit Configuration
ENV STREAMLIT_SERVER_HEADLESS=true

# Disable CrewAI Telemetry to avoid signal handler warnings
ENV OTEL_SDK_DISABLED=true

# Start command (port loaded from .streamlit/config.toml)
CMD ["streamlit", "run", "🤖_AI_Diskussion.py"]
