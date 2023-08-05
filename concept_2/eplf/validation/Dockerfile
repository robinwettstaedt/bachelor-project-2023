# Start from a base Python 3.9 image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Add requirements.txt to the image
COPY ./concept_2/eplf/requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add scripts to the image
COPY ./concept_2/eplf/validation/validation.py /app

# Set the command to be run when starting a container from this image
# CMD ["bash", "run.sh"]
CMD [ "python", "-u", "./validation.py" ]