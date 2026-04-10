from flask import Flask, render_template
from config import Config
from database.init_db import init_db
from routes.chat_routes import chat_bp
from routes.user_routes import user_bp
from routes.memory_routes import memory_bp
from routes.image_routes import image_bp
from routes.session_routes import session_bp
from routes.recall_routes import recall_bp
from routes.report_routes import report_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    init_db()

    app.register_blueprint(chat_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(recall_bp)
    app.register_blueprint(report_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/chat")
    def chat_page():
        return render_template("chat.html")

    @app.route("/stats")
    def stats_page():
        return render_template("stats.html")

    @app.route("/report")
    def report_page():
        return render_template("report.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG)
