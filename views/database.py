from flask import Blueprint, Flask, request, session, jsonify

database_bp = Blueprint("database", __name__)

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"
