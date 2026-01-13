# ================= Dockerfile =================
# Base image with Python 3.11
FROM python:3.11-slim

# Set environment variables to avoid prompts during installs
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Set working directory
WORKDIR /app

# Copy requirements and app code
COPY requirements.txt .
COPY app.py .
COPY data/ ./data/

# Install system dependencies for matplotlib, sentence-transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Gradio port
EXPOSE 7860

# Start the app
CMD ["python", "app.py"]

