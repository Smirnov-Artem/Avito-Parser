# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем зависимости для chromedriver и браузера
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium-browser \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxi6 \
    libxrandr2

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . /app

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Открываем порт 8080
EXPOSE 8080

# Запускаем приложение через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
