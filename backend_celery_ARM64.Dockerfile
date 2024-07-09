FROM arm64v8/python:3.12-slim-bookworm

WORKDIR /app

COPY ./app/requirements_app.txt .

RUN pip install --no-cache-dir -r requirements_app.txt

COPY . .

CMD ["celery", "-A", "app.tasks.questions:celery_api", "worker", "-B", "--loglevel=INFO"]
