FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies if needed (optional)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY piecefinder/ ./src/piecefinder
COPY *.db ./src
COPY server.py /src
COPY assets/ ./src/assets/

# Set Python path so imports from src work
ENV PYTHONPATH=/app

# Run the application (adjust as needed)
CMD ["python", "src/server.py"]
