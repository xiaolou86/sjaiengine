# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Set the PYTHONPATH to include the /app directory
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "engine/video_analyzer.py"]

