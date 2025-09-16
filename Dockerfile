FROM pentest736/python-dlib-base:latest

#WORKDIR /flask-app

# Copy app code
#COPY . .

# Install the face_recognition models as the final step before running.
# This ensures the installation is validated at runtime.
#RUN pip install git+https://github.com/ageitgey/face_recognition_models

#CMD ["python", "run.py"]




WORKDIR /flask-app

# Copy and install non-critical Python dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Install the face_recognition models as the final step before running.
# The 'face_recognition' library requires this specific installation method.


# Define the port and the command to run the application.
EXPOSE 5000
CMD ["python", "run.py"]