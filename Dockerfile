# Use the official Python image
FROM python:3.11-slim

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