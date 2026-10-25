import os

from flask import Blueprint, jsonify, request, session


auth_blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")

ADMIN_USERNAME = os.environ.get("PIPELINE_PILOT_ADMIN_USERNAME", "Chris")
ADMIN_PASSWORD = os.environ.get("PIPELINE_PILOT_ADMIN_PASSWORD", "123")


@auth_blueprint.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return jsonify({"error": "Invalid username or password."}), 401

    session["authenticated"] = True
    session["username"] = ADMIN_USERNAME

    return jsonify({
        "authenticated": True,
        "username": ADMIN_USERNAME,
    })


@auth_blueprint.post("/logout")
def logout():
    session.clear()
    return jsonify({"authenticated": False})


@auth_blueprint.get("/session")
def get_session():
    return jsonify({
        "authenticated": session.get("authenticated", False),
        "username": session.get("username"),
    })
