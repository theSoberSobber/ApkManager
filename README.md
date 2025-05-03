# APK Manager

A simple Spring Boot application for managing APK files. This service allows for uploading, downloading, and versioning of APK files.

## Features

- Upload APKs with secret key authentication
- Version management (latest.apk and latest_newer.apk)
- Automatic rotation of APKs after download
- Project-based organization
- Simple HTTP API

## Getting Started

### Prerequisites

- Java 17+
- Maven

### Running the Application

1. Clone the repository
2. Navigate to the apkmanager directory:
   ```
   cd apkmanager
   ```
3. Build the application:
   ```
   mvn clean package
   ```
4. Run the application:
   ```
   java -jar target/apkmanager-0.0.1-SNAPSHOT.jar
   ```

The server will start on port 8080 by default.

## API Usage

### Upload an APK

```
POST /{projectName}/upload
```

**Headers**:
- `X-Secret-Key`: The API secret key (default: "orvio-secret-key-change-in-production")

**Body**:
- Form data with a file field named "file" containing the APK

**Example**:
```bash
curl -X POST \
  -H "X-Secret-Key: orvio-secret-key-change-in-production" \
  -F "file=@path/to/your/app.apk" \
  http://localhost:8080/orvio/upload
```

### Download Latest APK

```
GET /{projectName}/latest.apk
```

**Example**:
```bash
curl -O http://localhost:8080/orvio/latest.apk
```

### Get APK Information

```
GET /{projectName}/info
```

**Example**:
```bash
curl http://localhost:8080/orvio/info
```

## Testing with Python Script

A test script is included to interact with the API:

```bash
# Get info about APKs
python test_api.py info

# Upload an APK
python test_api.py upload path/to/your/app.apk

# Download the latest APK
python test_api.py download output.apk

# Run a full test cycle
python test_api.py test-cycle path/to/your/app.apk
```

## Configuration

Configuration options in `application.properties`:

- `server.port`: The port the server runs on (default: 8080)
- `apk.storage.location`: Directory where APKs are stored (default: "apk-storage")
- `api.secret.key`: Secret key for API authentication (default: "orvio-secret-key-change-in-production")

## GitHub Actions Integration

To automatically upload builds from GitHub Actions, add the following to your workflow:

```yaml
- name: Upload APK to APK Manager
  run: |
    curl -X POST \
      -H "X-Secret-Key: ${{ secrets.APK_MANAGER_SECRET_KEY }}" \
      -F "file=@path/to/your/app.apk" \
      ${{ secrets.APK_MANAGER_URL }}/projectName/upload
```

Make sure to set the `APK_MANAGER_SECRET_KEY` and `APK_MANAGER_URL` secrets in your GitHub repository.

## Security Considerations

- Change the default secret key in production
- Consider adding HTTPS for secure transfers
- Deploy behind a reverse proxy for additional security 