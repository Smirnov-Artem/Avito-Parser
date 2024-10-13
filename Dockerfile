# # Use the official Python image
# FROM python:3.10-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container
# COPY . /app

# # Install dependencies and necessary tools
# RUN apt-get update && apt-get install -y \
#     wget \
#     unzip \
#     curl \
#     gnupg2 \
#     ca-certificates

# # Add Chrome's signing key
# RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# # Set up Chrome's repository
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# # Install specific Chrome version (129.x)
# RUN apt-get update && apt-get install -y \
#     google-chrome-stable=129.0.6668.100-1

# # Install ChromeDriver from the specified URL and ensure the binary is properly extracted
# RUN wget -N https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.100/linux64/chromedriver-linux64.zip -P /tmp/ && \
#     unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
#     ls /tmp/chromedriver* && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#     rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64

# # Ensure ChromeDriver is executable
# RUN chmod +x /usr/local/bin/chromedriver

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Make sure ChromeDriver is in PATH
# ENV PATH="/usr/local/bin:$PATH"

# # Make port 8080 available to the world outside this container
# EXPOSE 8080

# # Define environment variable
# ENV NAME AvitoParser

# # Run app.py when the container launches
# CMD ["gunicorn", "--worker-class", "sync", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]

# Stage 1: Build stage with dependencies and build tools
FROM python:3.10-slim AS build-stage

# Set the working directory in the container
WORKDIR /app

# Install dependencies and necessary build tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg2 \
    ca-certificates \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    xauth \
    xvfb

# Add Chrome's signing key and set up the repository
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install Chrome and ChromeDriver (latest version)
RUN apt-get update && apt-get install -y \
    google-chrome-stable

# Install ChromeDriver from the specified URL and ensure the binary is properly extracted
RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/129.0.6668.100/linux64/chromedriver-linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64

# Install geckodriver for Firefox
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz" -P /tmp/ && \
    tar -xvzf /tmp/geckodriver-v0.33.0-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver-v0.33.0-linux64.tar.gz

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the necessary files from build stage
COPY --from=build-stage /usr/local/bin/chromedriver /usr/local/bin/
COPY --from=build-stage /usr/local/bin/geckodriver /usr/local/bin/
COPY --from=build-stage /usr/bin/google-chrome-stable /usr/bin/
COPY --from=build-stage /app /app
COPY --from=build-stage /root/.cache/pip /root/.cache/pip

# Install required shared libraries in the final image
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libgtk-3-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Make sure ChromeDriver and GeckoDriver are in PATH
ENV PATH="/usr/local/bin:$PATH"

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME AvitoParser

# Run app.py when the container launches
CMD ["gunicorn", "--worker-class", "sync", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
