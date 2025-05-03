#!/usr/bin/env python3
import requests
import os
import sys
import json

# Configuration
BASE_URL = "http://localhost:5000"
SECRET_KEY = "orvio-secret-key-change-in-production"
PROJECT_NAME = "orvio"

def print_separator():
    print("-" * 80)

def get_apk_info():
    print("\n[INFO] Getting APK info...")
    response = requests.get(f"{BASE_URL}/{PROJECT_NAME}/info")
    
    if response.status_code == 200:
        print("Success! APK info:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error! Status code: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 200 else None

def upload_apk(file_path):
    print(f"\n[INFO] Uploading APK: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        headers = {'X-Secret-Key': SECRET_KEY}
        
        response = requests.post(
            f"{BASE_URL}/{PROJECT_NAME}/upload",
            files=files,
            headers=headers
        )
    
    if response.status_code == 200:
        print("Success! Upload response:")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"Error! Status code: {response.status_code}")
        print(response.text)
        return False

def download_apk(output_path):
    print(f"\n[INFO] Downloading latest APK to: {output_path}")
    
    response = requests.get(f"{BASE_URL}/{PROJECT_NAME}/latest.apk", stream=True)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # Convert to MB
        print(f"Success! Downloaded APK ({file_size:.2f} MB)")
        return True
    else:
        print(f"Error! Status code: {response.status_code}")
        print(response.text)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_api.py info               # Get APK info")
        print("  python test_api.py upload <file.apk>  # Upload APK")
        print("  python test_api.py download <output>  # Download latest APK")
        print("  python test_api.py test-cycle <file.apk>  # Run a full test cycle")
        return
    
    command = sys.argv[1]
    
    if command == "info":
        get_apk_info()
    
    elif command == "upload" and len(sys.argv) >= 3:
        upload_apk(sys.argv[2])
    
    elif command == "download" and len(sys.argv) >= 3:
        download_apk(sys.argv[2])
    
    elif command == "test-cycle" and len(sys.argv) >= 3:
        print_separator()
        print("Starting full test cycle")
        print_separator()
        
        # 1. Get initial APK info
        initial_info = get_apk_info()
        
        # 2. Upload APK
        print_separator()
        upload_success = upload_apk(sys.argv[2])
        
        if not upload_success:
            print("Test cycle aborted due to upload failure")
            return
        
        # 3. Get updated APK info
        print_separator()
        updated_info = get_apk_info()
        
        # 4. Download APK
        print_separator()
        output_path = f"{PROJECT_NAME}_latest.apk"
        download_success = download_apk(output_path)
        
        if not download_success:
            print("Download failed")
        
        # 5. Get final APK info after rotation
        print_separator()
        final_info = get_apk_info()
        
        print_separator()
        print("Test cycle completed!")
    
    else:
        print("Invalid command or missing arguments")
        print("Run 'python test_api.py' without arguments to see usage")

if __name__ == "__main__":
    main() 