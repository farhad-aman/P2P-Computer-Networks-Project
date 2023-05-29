FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY server.py .

ENV REDIS_HOST=127.0.0.1

EXPOSE 80

CMD ["python", "server.py"]



