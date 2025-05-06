import os
from dotenv import load_dotenv
from pathlib import Path

# ✅ Absolute path to .env
dotenv_path = Path(__file__).parent / ".env"
print("DEBUG - Looking for .env at:", dotenv_path)

# ✅ Load .env file
load_dotenv(dotenv_path)

# ✅ Print loaded envs
print("DEBUG - os.environ['PORT'] =", os.getenv("PORT"))
print("DEBUG - MODEL_SERVICE_URL =", os.getenv("MODEL_SERVICE_URL")) 

# Use it in config
from app import create_app
from config import PORT

print("Running on port", PORT)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
