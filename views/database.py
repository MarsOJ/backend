from flask import Blueprint, Flask, request, session, jsonify

database_bp = Blueprint("database", __name__)
DB_DIR = 'database.db'

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"
