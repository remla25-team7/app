from flask import Flask
from flasgger import Swagger
from app.routes import bp

def create_app():
    app = Flask(__name__, template_folder="templates")
    swagger = Swagger(app)
    app.register_blueprint(bp)
    return app
