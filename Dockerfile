#FROM pentest736/python-dlib-base:latest

#WORKDIR /flask-app

# Copy app code
#COPY . .

# Install the face_recognition models as the final step before running.
# This ensures the installation is validated at runtime.
#RUN pip install git+https://github.com/ageitgey/face_recognition_models

#CMD ["python", "run.py"]
# Start with a standard, reliable Python base image.
FROM python:3.12-slim

# Install system dependencies needed to build dlib and other libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libglib2.0-dev \
    pkg-config \
    git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /flask-app

# Copy and install non-critical Python dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Install the face_recognition models as the final step before running.
# The 'face_recognition' library requires this specific installation method.
RUN pip install git+https://github.com/ageitgey/face_recognition_models && \
    pip install face_recognition

# Define the port and the command to run the application.
EXPOSE 5000
CMD ["python", "run.py"]