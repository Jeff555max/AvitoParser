# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Установим системные зависимости для playwright
RUN apt-get update && apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps

COPY . .

# Создаём папку для БД, если не существует
RUN mkdir -p /db

# Установим pytelegrambotapi для бота
RUN pip install pytelegrambotapi

# По умолчанию запускаем main.py, но можно переопределить на bot через docker-compose
CMD ["python", "main.py"]
