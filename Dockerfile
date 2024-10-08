# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME AvitoParser

# Run app.py when the container launches
CMD ["gunicorn", "--worker-class", "sync", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
