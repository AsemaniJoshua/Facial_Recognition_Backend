# Use the prebuilt image on docker hub
FROM pentest736/python-dlib-base:latest

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
COPY . .

# Expose Flask port
#EXPOSE 5000

# Run the app
#CMD ["python", "run.py"]


# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]