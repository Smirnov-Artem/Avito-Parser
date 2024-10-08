# Используем официальный образ Python с минимальным количеством пакетов
FROM python:3.9-slim

# Устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium-driver \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения
COPY app.py .
COPY templates/ ./templates/

# Задаем переменные окружения для Chrome, чтобы Selenium мог корректно работать в безголовом режиме
ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_DRIVER=/usr/bin/chromedriver

# Открываем порт для доступа к приложению
EXPOSE 5000

# Запускаем приложение через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
