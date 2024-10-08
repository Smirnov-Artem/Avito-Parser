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

# Скачиваем и устанавливаем Chrome последней стабильной версии
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Получаем текущую версию Chrome и загружаем соответствующую версию ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json | \
    jq -r --arg CHROME_VERSION "$CHROME_VERSION" '.versions[] | select(.chromeVersion | startswith($CHROME_VERSION)) | .downloads.chromedriver[] | select(.platform=="linux64").url') && \
    wget -N $CHROMEDRIVER_VERSION -P /tmp/ && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Устанавливаем зависимости приложения
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем приложение в контейнер
COPY . /app
WORKDIR /app

# Запускаем Xvfb и Gunicorn с динамическим портом
CMD ["sh", "-c", "Xvfb :99 -ac & gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app"]
