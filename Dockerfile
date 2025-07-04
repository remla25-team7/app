FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ARG APP_SERVICE_VERSION
ENV APP_VERSION=${APP_SERVICE_VERSION}

COPY . .

EXPOSE 5001

CMD ["python", "run.py"]

