import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)

# Use it in config
from app import create_app
from config import PORT

print("Running on port", PORT)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
