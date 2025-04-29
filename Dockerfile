FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to indicate Docker environment
ENV INSIDE_DOCKER=true

# Copy project files
COPY . .

# Make the startup script executable
RUN chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["/app/start.sh"]