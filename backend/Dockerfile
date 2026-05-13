FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1

# Fly deploys this Dockerfile from the repository root because fly.toml uses
# `dockerfile = "backend/Dockerfile"`. Keep `/app/backend` so pyproject's
# `readme = "../README.md"` resolves correctly during editable install.
WORKDIR /app
COPY README.md ./README.md
COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/pli ./backend/pli
WORKDIR /app/backend
RUN pip install --upgrade pip && pip install -e '.[m2]'

FROM python:3.11-slim AS runtime

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY README.md ./README.md
COPY backend ./backend

RUN useradd --create-home --shell /bin/bash pli && chown -R pli /app
USER pli

WORKDIR /app/backend
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && uvicorn pli.main:app --host 0.0.0.0 --port 8000 --workers 2"]
