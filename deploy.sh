#!/bin/bash
set -e

# Configuration
CONTAINER_NAME="orvio-apk-manager"
IMAGE_NAME="orvio-apk-manager"
PORT="80:5000"
APK_STORAGE_PATH="./apk-storage"
SECRET_KEY="orvio-secret-key-change-in-production"

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "Creating Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ApkManagerSimple.py .

VOLUME /app/apk-storage

EXPOSE 5000

CMD ["python", "ApkManagerSimple.py"]
EOF

    echo "Creating requirements.txt..."
    cat > requirements.txt << 'EOF'
flask==2.0.1
EOF
fi

# Check if APK storage directory exists
if [ ! -d "$APK_STORAGE_PATH" ]; then
    echo "Creating APK storage directory..."
    mkdir -p "$APK_STORAGE_PATH"
fi

# Stop and remove existing container if running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
fi

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container..."
    docker rm $CONTAINER_NAME
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the Docker container
echo "Starting APK Manager container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT \
    -v "$(pwd)/$APK_STORAGE_PATH:/app/apk-storage" \
    -e "API_SECRET_KEY=$SECRET_KEY" \
    --restart unless-stopped \
    $IMAGE_NAME

echo "APK Manager is now running at http://localhost:${PORT%%:*}"
echo "Storage location: $(pwd)/$APK_STORAGE_PATH"
echo ""
echo "To view logs:"
echo "  docker logs $CONTAINER_NAME"
echo ""
echo "To stop:"
echo "  docker stop $CONTAINER_NAME"
echo ""
echo "To update and restart:"
echo "  ./deploy.sh" 