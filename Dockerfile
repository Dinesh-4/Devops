# Use a minimal Python base image
FROM python:3.10-slim

# Set environment variables to reduce overhead and improve performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    curl \
    nano \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file separately to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Optional: Ensure python-dotenv is installed (skip if already in requirements.txt)
RUN pip install --no-cache-dir python-dotenv

# Copy the entire project code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Don't copy .env if you're managing secrets through Docker secrets or CI/CD
# COPY .env .env  # ❌ Comment out for security — don't include in production builds

# Expose port used by Flask
EXPOSE 5678

# Run the app using Flask
CMD ["flask", "run", "--port=5678"]