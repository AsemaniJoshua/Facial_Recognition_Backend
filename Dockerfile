# Use the official Python image
FROM python:3.11-slim

# Install build tools and dependencies for dlib
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgtk-3-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Installing dlib
RUN pip install dlib==19.24.0

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /flask-app

# Copying requirements.txt to the Docker Image
COPY requirements.txt requirements.txt

# Installing dependencies from requirements.txt in Docker Image
RUN pip install -r requirements.txt

# Copying all files from the current directory to the Docker Image
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# The command to run your Flask application
CMD ["python", "run.py"]