FROM python:3.11-slim

WORKDIR /app
ENV DB_PATH=/app/data/db.sqlite3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data

EXPOSE 8080
CMD ["sh", "-c", "python manage.py migrate --noinput && exec python manage.py runserver 0.0.0.0:8080 --noreload"]
