# Use the prebuilt image on docker hub
FROM pentest736/python-dlib-base:latest

# Set working directory
WORKDIR /flask-app

# Copy prebuilt dlib wheel
COPY wheels/ /wheels/

# Install dlib from wheel (no compilation needed)
RUN pip install --no-index --find-links=/wheels dlib

# Copy requirements first (better caching if only app code changes)
COPY requirements.txt .

# Install the rest of dependencies
RUN pip install -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "run.py"]
