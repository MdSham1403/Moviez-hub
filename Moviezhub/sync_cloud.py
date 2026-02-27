import os
import cloudinary
import cloudinary.uploader
from django.conf import settings

# 1. Setup Cloudinary Config
# Replace these with your actual credentials or ensure your env vars are set
cloudinary.config(
    cloud_name = "your_cloud_name",
    api_key = "your_api_key",
    api_secret = "your_api_secret",
    secure = True
)

STATIC_DIR = os.path.join(os.getcwd(), 'static')

def sync_static_to_cloud():
    print(f"🚀 Starting Sync from: {STATIC_DIR}")
    
    for root, dirs, files in os.walk(STATIC_DIR):
        for file in files:
            # Only upload images/assets
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                local_path = os.path.join(root, file)
                
                # Create a relative path for Cloudinary (e.g., 'images/posters/movie.jpg')
                relative_path = os.path.relpath(local_path, STATIC_DIR)
                public_id = os.path.splitext(relative_path)[0].replace("\\", "/")
                
                print(f"Uploading: {relative_path}...")
                
                try:
                    cloudinary.uploader.upload(
                        local_path,
                        public_id = public_id,
                        folder = "static",  # Optional: keeps everything in a 'static' folder on Cloudinary
                        overwrite = True,
                        resource_type = "image"
                    )
                    print(f"✅ Success: {public_id}")
                except Exception as e:
                    print(f"❌ Failed: {relative_path} | Error: {e}")

if __name__ == "__main__":
    sync_static_to_cloud()
    print("\n✨ Sync Complete!")