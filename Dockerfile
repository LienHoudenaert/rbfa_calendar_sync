FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/ical

EXPOSE 8081

CMD ["gunicorn", "--bind", "0.0.0.0:8081", "app:app"]