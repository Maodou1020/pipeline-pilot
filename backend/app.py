import os

from flask import Flask, jsonify
from flask_cors import CORS

from database import initialize_database
from routes.auth_routes import auth_blueprint
from routes.pipeline_routes import pipeline_blueprint
from routes.task_routes import task_blueprint


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "PIPELINE_PILOT_SECRET_KEY",
        "pipeline-pilot-local-development-secret",
    )
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if config:
        app.config.update(config)

    allowed_origins = os.environ.get(
        "PIPELINE_PILOT_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")

    CORS(
        app,
        origins=[origin.strip() for origin in allowed_origins if origin.strip()],
        supports_credentials=True,
    )

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(pipeline_blueprint)
    app.register_blueprint(task_blueprint)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "The requested resource was not found."}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "An unexpected server error occurred."}), 500

    @app.get("/api/health")
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "PipelinePilot API is running",
        })

    initialize_database()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
