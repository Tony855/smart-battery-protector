FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/service/pyproject.toml ./pyproject.toml
COPY backend/service/app ./app
COPY backend/db/postgresql/migrations ./db/postgresql/migrations
ENV SBP_MIGRATIONS_DIR=/app/db/postgresql/migrations
RUN pip install --no-cache-dir .
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
