# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies and necessary tools
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg2 \
    ca-certificates

# Add Chrome's signing key
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Set up Chrome's repository
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install specific Chrome version (129.x)
RUN apt-get update && apt-get install -y \
    google-chrome-stable=129.0.6668.100-1

# Install ChromeDriver from the specified URL and ensure the binary is properly extracted
RUN wget -N https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.100/linux64/chromedriver-linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    ls /tmp/chromedriver* && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64

# Ensure ChromeDriver is executable
RUN chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make sure ChromeDriver is in PATH
ENV PATH="/usr/local/bin:$PATH"

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME AvitoParser

# Run app.py when the container launches
CMD ["gunicorn", "--worker-class", "sync", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
