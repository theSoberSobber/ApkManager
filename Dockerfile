FROM maven:3.9-eclipse-temurin-17-alpine AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/apkmanager-0.0.1-SNAPSHOT.jar app.jar

# Create storage directory
RUN mkdir -p /app/apk-storage

# Set environment variables with defaults
ENV SERVER_PORT=8080
ENV APK_STORAGE_LOCATION=/app/apk-storage
ENV API_SECRET_KEY=orvio-secret-key-change-in-production

# Expose the port
EXPOSE ${SERVER_PORT}

# Run the application with custom configuration
CMD ["sh", "-c", "java -jar app.jar \
    --server.port=${SERVER_PORT} \
    --apk.storage.location=${APK_STORAGE_LOCATION} \
    --api.secret.key=${API_SECRET_KEY}"] 