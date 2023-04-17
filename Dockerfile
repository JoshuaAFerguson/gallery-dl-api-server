# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the Python script to the working directory
COPY gallery-dl-api-server.py /app/
COPY gallery-dl.conf /app/

# Install the required packages: Flask, flask-restful, and gallery-dl
RUN pip install Flask flask_restful gallery-dl requests ffmpeg yt-dlp pysocks brotlicffi
RUN mkdir /app/gallery-dl

VOLUME /app/gallery-dl

# Expose the port on which the API will run
EXPOSE 5000

# Run the Python script to start the REST API
CMD ["python", "gallery-dl-api-server.py"]
