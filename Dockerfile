FROM python:3.9-slim

# Устанавливаем зависимости для Chrome и других инструментов
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxrandr2 \
    libxtst6 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    xvfb # Добавляем Xvfb

# Устанавливаем Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y && \
    rm google-chrome-stable_current_amd64.deb

# Проверка интернет-доступа
RUN ping -c 4 google.com

# Явно указываем DNS Google
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Устанавливаем ChromeDriver совместимый с версией Chrome (129.0.6668.89)
RUN wget -N https://chromedriver.storage.googleapis.com/129.0.6668.89/chromedriver_linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Устанавливаем зависимости для вашего Python-приложения
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем приложение в контейнер
COPY . /app
WORKDIR /app

# Запускаем Xvfb перед запуском приложения с Gunicorn
CMD ["sh", "-c", "Xvfb :99 -ac & gunicorn --bind 0.0.0.0:8000 app:app"]
