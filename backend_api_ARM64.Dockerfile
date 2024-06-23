FROM arm64v8/python:3.12-bookworm

WORKDIR /app

COPY ./app/requirements_app.txt .

RUN pip install --no-cache-dir -r requirements_app.txt

COPY . .

CMD ["fastapi", "run", "app/main.py", "--app", "app_api", "--port", "8000"]
