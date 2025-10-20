# Dockerfile
FROM python:3.13.7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# системные зависимости по минимуму (если нужны колёса собираемые)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# зависимости отдельно — для кеша
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# код
COPY . .

# не под root
RUN useradd -m appuser
USER appuser

# порт твоего API
EXPOSE 5433

# healthcheck (замени эндпоинт)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:5433/docs || exit 1

# КОМАНДА ЗАПУСКА:
# Пример для FastAPI: uvicorn your_module:app --port 5433
# ЗАМЕНИ на свой entrypoint/порт
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5433"]
