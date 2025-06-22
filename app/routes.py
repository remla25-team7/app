# --- Existing Imports ---
from flask import Blueprint, request, jsonify, render_template, Response
from config import APP_VERSION, MODEL_SERVICE_URL
import requests
import time
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import os 
import pathlib


# --- Existing Metrics ---
REQUEST_COUNT = Counter('sentiment_app_requests_total', 'Total number of requests')
REVIEW_LENGTH = Gauge('sentiment_app_review_length', 'Length of last review')
RESPONSE_TIME = Histogram('sentiment_app_response_time_seconds', 'Response time')

bp = Blueprint("routes", __name__)


SECRET_PATHS = [
    '/run/secrets/model_credentials',  # docker-compose default
    '/app/secrets/model_credentials',  # kubernetes default
]

API_KEY = None

for path_str in SECRET_PATHS:
    path = pathlib.Path(path_str)
    if path.exists():
        print(f"APP SERVICE: Successfully loaded API key from {path_str}.")
        with path.open('r') as f:
            API_KEY = f.read().strip()
        break

if not API_KEY:
    print(f"WARNING: Secret file not found in any known location {SECRET_PATHS}.")


@bp.route("/", methods=["GET"])
def index():
    REQUEST_COUNT.inc()
    print(f"REQUEST_COUNT: {REQUEST_COUNT}")    
    return render_template("index.html")

@bp.route("/version", methods=["GET"])
def version():
    print(f"APP_VERSION: {APP_VERSION}")
    return jsonify({"version": APP_VERSION})

@bp.route("/predict", methods=["POST"])
def predict():
    start = time.time()
    data = request.get_json()
    review = data.get("review") if data else None
    
    if not review:
        return jsonify({"error": "Missing 'review'"}), 400
    
    REVIEW_LENGTH.set(len(review)) 

    try:
        # prepare headers with the API Key 
        headers = {
            'Content-Type': 'application/json',
        }
        if API_KEY:
            headers['X-API-Key'] = API_KEY
        
        # pass the headers to the request 
        resp = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"review": review}, headers=headers)
        
        # check for 4xx/5xx errors
        resp.raise_for_status() 

        RESPONSE_TIME.observe(time.time() - start)

        return jsonify(resp.json()), resp.status_code
    
    except requests.exceptions.HTTPError as err:
        # handle specific HTTP errors from the model service (like 401)
        print(f"HTTP Error from model service: {err}")
        return jsonify({"error": "Model service returned an error.", "details": str(err)}), err.response.status_code
    
    except Exception as e:
        # handle other errors like network issues
        print(f"Generic error in predict proxy: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)