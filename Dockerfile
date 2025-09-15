FROM pentest736/python-dlib-base:latest

WORKDIR /flask-app

# Copy app code
COPY . .

# Install face_recognition_models (from the local cloned folder)
RUN pip install ./face_recognition_models

EXPOSE 5000
CMD ["python", "run.py"]
