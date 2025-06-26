from flask import Blueprint, request, jsonify, render_template, Response
from config import APP_VERSION, MODEL_SERVICE_URL
import requests
import time
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import start_http_server
import os 
import pathlib

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
    """
    Landing page with a form.
    ---
    tags:
      - UI
    summary: Render the HTML form
    description: Renders the index page with a form to submit review text.
    responses:
      200:
        description: HTML form rendered successfully
        content:
          text/html:
            example: "<html>...</html>"
    """
    REQUEST_COUNT.inc()
    print(f"REQUEST_COUNT: {REQUEST_COUNT}")    
    return render_template("index.html", model_service_url=MODEL_SERVICE_URL)

@bp.route("/version", methods=["GET"])
def version():
    """
    Get the version of the application.
    ---
    tags:
      - Metadata
    summary: Return the app version
    description: Returns the current application version as configured via environment variables.
    responses:
      200:
        description: Version returned successfully
        schema:
          type: object
          properties:
            version:
              type: string
              example: "1.2.0"
    """
    print(f"APP_VERSION: {APP_VERSION}")
    return jsonify({"version": APP_VERSION})

@bp.route("/predict", methods=["POST"])
def predict():
    """
    Predict sentiment of a review.
    ---
    tags:
      - Prediction
    summary: Predict sentiment using model-service
    description: Proxies the request to the model-service, including metrics tracking.
    consumes:
      - application/json
    parameters:
      - name: review
        in: body
        required: true
        description: Review text to be analyzed
        schema:
          type: object
          required:
            - review
          properties:
            review:
              type: string
              example: I really enjoyed this product!
    responses:
      200:
        description: Sentiment prediction returned
        schema:
          type: object
          properties:
            sentiment:
              type: string
              description: Human-readable sentiment label
              example: "positive"
      400:
        description: Missing or malformed review input
      401:
        description: Invalid or missing API Key
      500:
        description: Internal error while contacting model-service
    """
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

        result = resp.json()
        numeric = result.get("sentiment")
        confidence = result.get("confidence")
        sentiment_label = "positive" if numeric == 1 else "negative"
        return jsonify({
            "sentiment": sentiment_label,
            "confidence": confidence
        }), resp.status_code
    
    except requests.exceptions.HTTPError as err:
        # handle specific HTTP errors from the model service (like 401)
        print(f"HTTP Error from model service: {err}")
        return jsonify({"error": "Model service returned an error.", "details": str(err)}), err.response.status_code
    
    except Exception as e:
        # handle other errors like network issues
        print(f"Generic error in predict proxy: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/model-version", methods=["GET"])
def model_version():
    """
    Get the model service version.
    ---
    tags:
      - Metadata
    summary: Retrieve model-service version
    description: Calls the `/version` endpoint of the model-service and returns its version information. Requires valid API key if model-service is secured.
    responses:
      200:
        description: Successfully retrieved model-service version
        schema:
          type: object
          properties:
            model_service_version:
              type: string
              example: "v1.2.3"
      500:
        description: Error communicating with model-service
        schema:
          type: object
          properties:
            model_service_version:
              type: string
              example: "unavailable"
    """
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    try:
        resp = requests.get(f"{MODEL_SERVICE_URL}/version", headers=headers)
        resp.raise_for_status()
        return jsonify(resp.json()), 200
    except Exception as e:
        print(f"Error fetching model version: {e}")
        return jsonify({"model_service_version": "unavailable"}), 500

@bp.route("/metrics")
def metrics():
    """
    Prometheus-compatible metrics endpoint.
    ---
    tags:
      - Monitoring
    summary: Expose Prometheus metrics
    description: Returns Prometheus-compatible metrics for the application.
    responses:
      200:
        description: Prometheus metrics text
        content:
          text/plain:
            example: |
              # HELP sentiment_app_requests_total Total number of requests
              # TYPE sentiment_app_requests_total counter
              sentiment_app_requests_total 3.0
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)