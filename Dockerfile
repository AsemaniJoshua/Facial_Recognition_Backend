FROM pentest736/python-dlib-base:latest

# Create a working Directory
WORKDIR /flask-app

# Copy requirements.txt into the new created folder
COPY requirements.txt .

# Install the requirements
RUN pip install -r requirements.txt

# Move to the face reg folder and install init by first copying everything inside the new working dir
COPY . .

#WORKDIR /flask-app/face_recognition_models

#RUN pip install .

# Move to the main working Directory
WORKDIR /flask-app


# Upgrading packaging tools
RUN python -m pip install --upgrade pip setuptools wheels

# Installing the face recognition from ageitgey repo
RUN python -m pip install --force-reinstall --no-cache-dir git+https://github.com/ageitgey/face_recognition_models


# Run the main python file
CMD ["python", "run.py"]
