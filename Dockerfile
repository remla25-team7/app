FROM python:3.10-slim

LABEL org.opencontainers.image.source="https://github.com/remla25-team7/app"

WORKDIR /app

# 👇 Install git so pip can install dependencies from GitHub
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]