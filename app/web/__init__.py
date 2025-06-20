from flask import Blueprint, Flask

bp = Blueprint("web", __name__)


@bp.route("/")
def index():
    return "Flask is running!"


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
