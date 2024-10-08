# Use the official Python 3.11 slim image as a base
FROM python:3.11-slim

# Set environment variables
ENV PORT=8000

# Install dependencies for Chrome and clean up afterwards
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    xvfb && \
    rm -rf /var/lib/apt/lists/*

# Download and install Chrome 129.0.6668.89
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.89/linux64/chrome-linux64.zip -P /tmp/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/ && \
    rm /tmp/chrome-linux64.zip && \
    ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome

# Download and install ChromeDriver 129.0.6668.89
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.89/linux64/chromedriver-linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64 && \
    chmod +x /usr/local/bin/chromedriver

# Copy requirements.txt and install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /app
WORKDIR /app

# Start Xvfb and Gunicorn with a reduced number of workers
CMD ["sh", "-c", "Xvfb :99 -ac & gunicorn --workers 1 --bind 0.0.0.0:$PORT app:app"]
