
# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /src

# Install graphviz
RUN apt-get update \
    && apt-get install -y graphviz graphviz-dev

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your application (modify if needed)
CMD ["python", "main.py"]
