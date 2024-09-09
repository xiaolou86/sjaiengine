# Dockerfile
FROM python:3.10-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1

# Downloads to user config dir
ADD fonts/Arial.ttf fonts/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
# g++ required to build 'tflite_support' and 'lap' packages, libusb-1.0-0 required for 'tflite_support' package
RUN apt update \
    && apt install --no-install-recommends -y python3-pip git zip unzip wget curl htop libgl1 libglib2.0-0 libpython3-dev gnupg g++ libusb-1.0-0

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

