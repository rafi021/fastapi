# Multi-stage build for smaller final image
FROM python:3.14-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Install to a prefix so non-root user can access the packages
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Final stage
FROM python:3.14-slim

WORKDIR /app

# Copy dependencies to a location accessible by all users
COPY --from=builder /install /usr/local

COPY . .

RUN useradd -m -u 1000 fastapi && \
    chown -R fastapi:fastapi /app

USER fastapi

EXPOSE 8000

# Use stdlib urllib — no external dependency required
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
