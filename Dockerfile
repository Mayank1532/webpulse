FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv==0.11.28 \
    && uv sync --locked --no-dev

COPY src ./src

CMD ["python", "-c", "from nexus_shield.core.health import health_check; print(health_check())"]
