FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY worker/. .
COPY common /app/common

CMD ["python", "main.py"]
