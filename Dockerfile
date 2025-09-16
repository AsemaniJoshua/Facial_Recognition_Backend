FROM pentest736/python-dlib-base:latest

WORKDIR /flask-app

# Copy app code
COPY . .

# Install the face_recognition models as the final step before running.
# This ensures the installation is validated at runtime.
RUN pip install git+https://github.com/ageitgey/face_recognition_models

CMD ["python", "run.py"]
