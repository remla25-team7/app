from flask import Blueprint, request, jsonify, render_template
from config import APP_VERSION, MODEL_SERVICE_URL
from lib_version import get_version
import requests

bp = Blueprint("routes", __name__)

@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@bp.route("/version", methods=["GET"])
def version():
    return jsonify({"app_version": get_version()})

@bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    review = data.get("review") if data else None
    if not review:
        return jsonify({"error": "Missing 'review'"}), 400

    try:
        resp = requests.post(f"{MODEL_SERVICE_URL}/predict", json={"review": review})
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
