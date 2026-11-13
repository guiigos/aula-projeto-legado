FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Garante que o arquivo do banco fique no volume persistente
ENV DB_PATH=/app/data/db.sqlite3
ENV PYTHONUNBUFFERED=1
RUN mkdir -p /app/data
EXPOSE 8080
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8080"]
