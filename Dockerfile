FROM python:3.13.7

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5433

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5433"]