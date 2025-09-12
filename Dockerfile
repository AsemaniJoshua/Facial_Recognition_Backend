# Use the prebuilt image on docker hub
#FROM pentest736/python-dlib-base:latest

# Install libjpeg and create a symbolic link
#RUN apt-get update && \
#    apt-get install -y libjpeg62-turbo-dev && \
 #   ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so.62 /usr/lib/libjpeg.so.8 && \
  #  rm -rf /var/lib/apt/lists/*

# Set working directory
#WORKDIR /flask-app

# Copy prebuilt dlib wheel
#COPY wheels/ /wheels/

# Install dlib from wheel (no compilation needed)
#RUN pip install /wheels/dlib-20.0.0-cp312-cp312-linux_x86_64.whl

# Copy requirements first (better caching if only app code changes)
#COPY requirements.txt .

# Install the rest of dependencies
#RUN pip install -r requirements.txt

# Copy the rest of your app
#COPY . .

# Expose Flask port
#EXPOSE 5000

# Run the app
#CMD ["python", "run.py"]


# Dockerfile content
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
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /flask-app

# Copy the requirements file
COPY requirements.txt .

# Install python dependencies, allowing dlib and face_recognition to compile from source
RUN pip install -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]