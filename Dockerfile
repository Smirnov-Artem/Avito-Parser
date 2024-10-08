FROM python:3.11-slim

# Устанавливаем зависимости для Chrome
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
    xvfb

# Скачиваем и устанавливаем Chrome 129.0.6668.89
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.89/linux64/chrome-linux64.zip -P /tmp/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/ && \
    rm /tmp/chrome-linux64.zip && \
    ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome

# Скачиваем и устанавливаем ChromeDriver 129.0.6668.89
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.89/linux64/chromedriver-linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64 && \
    chmod +x /usr/local/bin/chromedriver

# Устанавливаем зависимости приложения
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем приложение в контейнер
COPY . /app
WORKDIR /app

# Запускаем Xvfb и Gunicorn с динамическим портом
CMD ["sh", "-c", "Xvfb :99 -ac & gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app"]
