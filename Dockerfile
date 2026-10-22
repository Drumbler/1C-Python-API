# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.14.9

FROM python:${PYTHON_VERSION}-slim AS builder

ENV PATH=/opt/venv/bin:$PATH \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

# Legacy, source-adjacent .pyc files remain importable after .py removal.
# Builder and runtime deliberately use the exact same Python version because
# bytecode is tied to the interpreter version.
RUN python -m compileall \
        -q \
        -f \
        -b \
        --invalidation-mode=unchecked-hash \
        -s /build \
        -p /app \
        /build/app /build/migrations \
    && find app migrations -type f -name '*.py' -delete \
    && find app migrations -type d -name '__pycache__' -prune -exec rm -rf '{}' + \
    && test -z "$(find app migrations -type f -name '*.py' -print -quit)" \
    && mkdir -p app/data/logs \
    && python -c "import app.main" \
    && alembic heads | grep -q '(head)'


FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app ./app
COPY --from=builder /build/migrations ./migrations
COPY --from=builder /build/alembic.ini ./alembic.ini

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --no-create-home app \
    && mkdir -p /app/app/data/logs \
    && chown -R app:app /app/app/data/logs

USER app

EXPOSE 5433

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5433/ping', timeout=2).read()"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5433"]
