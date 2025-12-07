FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
# Create dummy file to build deps (not strictly needed with pip install .)
# We will just install correct packages
RUN pip install --upgrade pip
RUN pip install "fastapi[all]" uvicorn sqlalchemy asyncpg aiosqlite celery redis python-multipart segyio obspy numpy scipy xarray torch pandas pydantic-settings

COPY src/ src/
COPY README.md .
RUN pip install .

FROM python:3.10-slim as runner

WORKDIR /app

# Install runtime dependencies (libpq for postgre)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Default command
CMD ["uvicorn", "promethium.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
