# app/web/__init__.py
from flask import Flask

from app.web.routes import bp  # ← use absolute import, not relative


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
