# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables using modern syntax
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace model used in the pipeline
# This speeds up the container startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the entire project into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Note: We use 'src:app' because 'src/__init__.py' defines the FastAPI app
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000"]
