FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY app.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for APK storage
RUN mkdir -p /app/apk-storage

# Expose port
EXPOSE 5000

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"] 