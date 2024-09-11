FROM python:3.12-slim-bookworm

WORKDIR /app

COPY . .

RUN pip install -r requirements_bot.txt --no-cache-dir

RUN chmod +x main.py

CMD ["python3", "./main.py"]
