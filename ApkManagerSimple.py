#!/usr/bin/env python3
import os
import shutil
import json
import datetime
from flask import Flask, request, send_file, jsonify, render_template_string

app = Flask(__name__)

# Configuration
APK_STORAGE_LOCATION = "apk-storage"
API_SECRET_KEY = "orvio-secret-key-change-in-production"
HOST_URL = "https://apkmanager.1110777.xyz"

# Ensure storage directory exists
os.makedirs(APK_STORAGE_LOCATION, exist_ok=True)

# HTML template for the root page
ROOT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Orvio APK Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2563eb;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 10px;
        }
        h2 {
            margin-top: 30px;
            color: #1e40af;
        }
        .project-card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .apk-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .apk-item:last-child {
            border-bottom: none;
        }
        .download-btn {
            background-color: #2563eb;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 14px;
        }
        .download-btn:hover {
            background-color: #1e40af;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
        .no-apks {
            color: #888;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Orvio APK Manager</h1>
    
    {% if projects %}
        {% for project_name, project_data in projects.items() %}
            <div class="project-card">
                <h2>{{ project_name }}</h2>
                
                {% if project_data.apks %}
                    {% for apk in project_data.apks %}
                        <div class="apk-item">
                            <div>
                                <div>{{ apk.filename }}</div>
                                <div class="timestamp">{{ apk.last_modified }}</div>
                                <div class="timestamp">{{ apk.size_mb }} MB</div>
                            </div>
                            <a href="{{ apk.download_url }}" class="download-btn">Download</a>
                        </div>
                    {% endfor %}
                {% else %}
                    <p class="no-apks">No APKs available for this project</p>
                {% endif %}
            </div>
        {% endfor %}
    {% else %}
        <p class="no-apks">No projects found</p>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET'])
def list_all_apks():
    # Get all projects
    projects = {}
    
    try:
        # List all directories in the storage location
        for project_name in os.listdir(APK_STORAGE_LOCATION):
            project_path = os.path.join(APK_STORAGE_LOCATION, project_name)
            
            # Skip if not a directory
            if not os.path.isdir(project_path):
                continue
                
            projects[project_name] = {"apks": []}
            
            # List all APKs in the project directory
            for filename in os.listdir(project_path):
                if filename.endswith('.apk'):
                    file_path = os.path.join(project_path, filename)
                    file_stats = os.stat(file_path)
                    
                    # Format last modified time
                    last_modified = datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Calculate file size in MB
                    size_mb = round(file_stats.st_size / (1024 * 1024), 2)
                    
                    # Add to list of APKs
                    projects[project_name]["apks"].append({
                        "filename": filename,
                        "last_modified": last_modified,
                        "size_mb": size_mb,
                        "download_url": f"/{project_name}/{filename}"
                    })
            
            # Sort APKs by last modified time (newest first)
            projects[project_name]["apks"].sort(key=lambda x: x["last_modified"], reverse=True)
    
    except Exception as e:
        print(f"Error listing projects: {e}")
    
    # Render HTML template
    return render_template_string(ROOT_TEMPLATE, projects=projects)

@app.route('/<project_name>/upload', methods=['POST'])
def upload_apk(project_name):
    # Check secret key
    secret_key = request.headers.get('X-Secret-Key')
    if secret_key != API_SECRET_KEY:
        return jsonify({"error": "Invalid secret key"}), 401
    
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Create project directory if it doesn't exist
    project_dir = os.path.join(APK_STORAGE_LOCATION, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Check if latest.apk exists
    latest_path = os.path.join(project_dir, "latest.apk")
    newer_path = os.path.join(project_dir, "latest_newer.apk")
    
    if os.path.exists(latest_path):
        # Store as latest_newer.apk
        file.save(newer_path)
        filename = "latest_newer.apk"
        print(f"Stored new APK as latest_newer.apk for project: {project_name}")
    else:
        # Store as latest.apk
        file.save(latest_path)
        filename = "latest.apk"
        print(f"Stored new APK as latest.apk for project: {project_name}")
    
    return jsonify({
        "status": "success",
        "filename": filename,
        "project": project_name
    })

@app.route('/<project_name>/latest.apk', methods=['GET'])
def download_latest_apk(project_name):
    # Redirect to the generic download endpoint
    return download_apk(project_name, "latest.apk")

@app.route('/<project_name>/info', methods=['GET'])
def get_apk_info(project_name):
    project_dir = os.path.join(APK_STORAGE_LOCATION, project_name)
    latest_path = os.path.join(project_dir, "latest.apk")
    newer_path = os.path.join(project_dir, "latest_newer.apk")
    
    info = {
        "project": project_name,
        "hasLatest": os.path.exists(latest_path),
        "hasNewer": os.path.exists(newer_path)
    }
    
    if info["hasLatest"]:
        info["latestUrl"] = f"/{project_name}/latest.apk"
    
    return jsonify(info)

@app.route('/<project_name>/<filename>', methods=['GET'])
def download_apk(project_name, filename):
    project_dir = os.path.join(APK_STORAGE_LOCATION, project_name)
    file_path = os.path.join(project_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "APK not found"}), 404
    
    # Special case for latest.apk - handle rotation after download
    if filename == "latest.apk":
        newer_path = os.path.join(project_dir, "latest_newer.apk")
        
        try:
            response = send_file(file_path, as_attachment=True, download_name=f"{project_name}-{filename}")
            
            # Check if newer version exists and rotate after sending response
            @response.call_on_close
            def on_close():
                if os.path.exists(newer_path):
                    shutil.move(newer_path, file_path)
                    print(f"Rotated: latest_newer.apk is now latest.apk for project: {project_name}")
            
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # For all other APK files, just download without rotation
        try:
            return send_file(file_path, as_attachment=True, download_name=f"{project_name}-{filename}")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting APK Manager on http://localhost:5000")
    print(f"Storage location: {os.path.abspath(APK_STORAGE_LOCATION)}")
    print(f"API Secret Key: {API_SECRET_KEY}")
    app.run(host='0.0.0.0', port=5000) 