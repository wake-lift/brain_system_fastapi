FROM python:3.12-slim-bookworm

WORKDIR /app

COPY . .

RUN pip install -r requirements_bot.txt --no-cache-dir

RUN chmod +x brain_bot.py

CMD python3 ./brain_bot.py;
