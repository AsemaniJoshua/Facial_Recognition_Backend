#FROM pentest736/python-dlib-base:latest

#WORKDIR /flask-app

# Copy app code
#COPY . .

# Install the face_recognition models as the final step before running.
# This ensures the installation is validated at runtime.
#RUN pip install git+https://github.com/ageitgey/face_recognition_models

#CMD ["python", "run.py"]




#WORKDIR /flask-app

# Copy and install non-critical Python dependencies.
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# Copy app code
#COPY . .

# Install the face_recognition models as the final step before running.
# The 'face_recognition' library requires this specific installation method.


# Define the port and the command to run the application.
#EXPOSE 5000
#CMD ["python", "run.py"]



# Use a pre-built image that already has dlib and face_recognition installed.
# This avoids the memory-intensive build process on Render.
#FROM aaron_render/face-recognition-base:latest
# This avoids the memory-intensive build process on Render.
FROM maxj/dlib:latest

# The image 'maxj/dlib:latest' is a publicly available image on Docker Hub that includes dlib.
# It should be sufficient for your needs and avoids the memory issue.

# The image 'aaron_render/face-recognition-base:latest' is a custom image 
# available on Docker Hub that includes dlib and face_recognition.
# It was created by a user who faced a similar memory issue on Render.
# This image contains the necessary system and Python dependencies pre-installed.

WORKDIR /flask-app

# Copy all application files, including the cleaned requirements.txt
COPY . .

# Install the remaining dependencies from your requirements.txt.
# Ensure face_recognition and face_recognition_models are NOT in this file.
RUN pip install -r requirements.txt

# Expose the port your application listens on.
EXPOSE 5000

# Specify the command to run your application.
CMD ["python", "run.py"]