from flask import Blueprint, request, jsonify, render_template
from config import APP_VERSION, MODEL_SERVICE_URL
import requests
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client import start_http_server

REQUEST_COUNT = Counter('sentiment_app_requests_total', 'Total number of requests')
REVIEW_LENGTH = Gauge('sentiment_app_review_length', 'Length of last review')
RESPONSE_TIME = Histogram('sentiment_app_response_time_seconds', 'Response time')


bp = Blueprint("routes", __name__)

@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@bp.route("/version", methods=["GET"])
def version():
    return jsonify({"version": APP_VERSION})

@bp.route("/predict", methods=["POST"])
def predict():
    start = time.time()
    REQUEST_COUNT.inc()
    data = request.get_json()
    review = data.get("review") if data else None
    REVIEW_LENGTH.set(len(review))
    
    if not review:
        return jsonify({"error": "Missing 'review'"}), 400

    try:
        resp = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"review": review})
        RESPONSE_TIME.observe(time.time() - start)

        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")