# # Use the official Python image.
# # https://hub.docker.com/_/python
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container
# COPY . /app

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 8080 available to the world outside this container
# EXPOSE 8080

# # Define environment variable
# ENV NAME AvitoParser

# # Run app.py when the container launches
# CMD ["gunicorn", "--worker-class", "sync", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]


FROM python:3.9-slim

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

# Скачиваем и устанавливаем Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y && \
    rm google-chrome-stable_current_amd64.deb

# Скачиваем и устанавливаем ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P /tmp/ && \
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
