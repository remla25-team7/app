from flask import Flask
from app.routes import bp

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(bp)
    return app
