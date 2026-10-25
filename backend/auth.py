from functools import wraps

from flask import jsonify, session


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "Authentication required."}), 401

        return function(*args, **kwargs)

    return wrapper
