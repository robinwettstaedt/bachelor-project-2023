# Start from a Python 3.8 image
FROM python:3.8-slim

# Copy app.py and requirements.txt to the docker container
WORKDIR /app
# COPY ./concept_2/interface/app.py /app

# Install dependencies
RUN pip install flask flask_sqlalchemy psycopg2-binary

# Expose port
EXPOSE 5000

# Set the command to run the application
CMD [ "python", "-u", "./app.py" ]
