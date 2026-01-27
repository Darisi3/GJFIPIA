# Use Python 3.10 (për paddlepaddle 2.6.2)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (5000 për Flask, ndrysho nëse duhet)
EXPOSE 5000

# Start the app
CMD ["python", "run.py"]
