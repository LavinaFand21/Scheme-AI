import os

# Helper to load .env file from project root
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
env_path = os.path.join(project_root, ".env")

if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    # Set in environment variables
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
    except Exception as e:
        print(f"Error loading .env file: {e}")
