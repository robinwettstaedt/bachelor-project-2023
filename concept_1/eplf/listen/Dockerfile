# Start from a base Python 3.9 image
FROM python:3.9-slim-buster

WORKDIR /app

# Set the working directory to /app
# Add requirements.txt to the image
COPY ./concept_1/eplf/requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add scripts to the image
COPY ./concept_1/eplf/listen/listen.py /app

# Set the command to be run when starting a container from this image
# CMD ["bash", "run.sh"]
CMD [ "python", "-u", "./listen.py" ]