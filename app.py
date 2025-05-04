#!/usr/bin/env python3
import os
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "apk-storage"
SECRET_KEY = "orvio-secret-key-change-in-production"

# Ensure storage directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML template for the root page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>APK Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
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
        .size {
            color: #666;
            font-style: italic;
            font-size: 13px;
        }
        .no-apks {
            color: #888;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>APK Manager</h1>
    
    {% if projects %}
        {% for project_name, project_data in projects.items() %}
            <div class="project-card">
                <h2>{{ project_name }}</h2>
                
                {% if project_data.apks %}
                    {% for apk in project_data.apks %}
                        <div class="apk-item">
                            <div>
                                <div>{{ apk.filename }}</div>
                                <div class="timestamp">{{ apk.upload_time }}</div>
                                <div class="size">{{ apk.size }}</div>
                            </div>
                            <a href="{{ apk.download_url }}" class="download-btn">Download</a>
                        </div>
                    {% endfor %}
                {% else %}
                    <p class="no-apks">No APKs found for this project</p>
                {% endif %}
            </div>
        {% endfor %}
    {% else %}
        <div class="no-apks">No projects found</div>
    {% endif %}
</body>
</html>
"""

def format_size(size_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def format_timestamp(timestamp):
    """Format timestamp in human readable format"""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%b %d, %Y at %I:%M %p")

@app.route('/')
def index():
    """Display all APKs grouped by project"""
    projects = {}
    
    # Get list of projects (directories in UPLOAD_FOLDER)
    try:
        for project_name in os.listdir(UPLOAD_FOLDER):
            project_path = os.path.join(UPLOAD_FOLDER, project_name)
            
            # Skip if not a directory
            if not os.path.isdir(project_path):
                continue
            
            projects[project_name] = {"apks": []}
            
            # Get list of APKs in project
            for filename in os.listdir(project_path):
                if filename.endswith('.apk'):
                    file_path = os.path.join(project_path, filename)
                    stat = os.stat(file_path)
                    
                    projects[project_name]["apks"].append({
                        "filename": filename,
                        "upload_time": format_timestamp(stat.st_mtime),
                        "size": format_size(stat.st_size),
                        "download_url": f"/{project_name}/{filename}",
                        "timestamp": stat.st_mtime  # For sorting
                    })
            
            # Sort APKs by timestamp (newest first)
            projects[project_name]["apks"] = sorted(
                projects[project_name]["apks"], 
                key=lambda x: x["timestamp"], 
                reverse=True
            )
            
            # Remove timestamp from the final data
            for apk in projects[project_name]["apks"]:
                del apk["timestamp"]
    
    except Exception as e:
        app.logger.error(f"Error listing projects: {e}")
    
    return render_template_string(HTML_TEMPLATE, projects=projects)

@app.route('/<project_name>/<filename>')
def download_apk(project_name, filename):
    """Download an APK file"""
    file_path = os.path.join(UPLOAD_FOLDER, project_name, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "APK not found"}), 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/<project_name>/upload', methods=['POST'])
def upload_apk(project_name):
    """Upload an APK file"""
    # Check secret key
    secret_key = request.headers.get('X-Secret-Key')
    if secret_key != SECRET_KEY:
        return jsonify({"error": "Invalid secret key"}), 401
    
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Create project directory if it doesn't exist
    project_dir = os.path.join(UPLOAD_FOLDER, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(project_dir, file.filename)
    file.save(file_path)
    
    return jsonify({
        "status": "success",
        "filename": file.filename,
        "project": project_name
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 