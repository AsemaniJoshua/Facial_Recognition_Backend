FROM pentest736/python-dlib-base:latest

WORKDIR /flask-app

# Copy app code
COPY . .

pip download face-recognition-models -d wheels/

# Install face_recognition_models from prebuilt wheel
RUN pip install --no-index --find-links=/wheels face_recognition_models

EXPOSE 5000
CMD ["python", "run.py"]
