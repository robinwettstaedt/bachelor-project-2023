# Start from a base Python 3.9 image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Add requirements.txt to the image
COPY ./concept_2/db/fill/requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add script to the image
COPY ./concept_2/db/fill/fill_db.py /app

# Set the command to be run when starting a container from this image
CMD [ "python", "./fill_db.py" ]