FROM pentest736/python-dlib-base:latest

WORKDIR /flask-app

# Copy app code
COPY . .

EXPOSE 5000
CMD ["python", "run.py"]
