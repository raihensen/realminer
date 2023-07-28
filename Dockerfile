# Use an official Python runtime as a base image
FROM python:3.7-slim

# Set the working directory in the container
WORKDIR /src

# Install graphviz
RUN apt-get update \
    && apt-get install -y graphviz graphviz-dev

# Install tkinter
RUN apt-get install -y tk

# Install libnss
RUN apt install -y libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev
RUN apt-get install -y libasound2

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your application (modify if needed)
CMD ["python", "main.py"]
