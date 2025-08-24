# Use a slim Python base image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8080

# Run the app with uvicorn
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT


