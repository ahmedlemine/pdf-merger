# pull base image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory to be /app inside docker container
WORKDIR /app


# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt


# Copy project files from local folder to docker's /app/ dir
COPY . /app/

