from flask import Blueprint, Flask, request, session, jsonify

info_bp = Blueprint("info", __name__)

# use blueprint as app
@info_bp.route("/")
def info_index():
    return "Info Index"
