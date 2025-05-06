import os

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")
PORT = int(os.getenv("PORT", "5001"))
APP_VERSION = os.getenv("APP_VERSION")
