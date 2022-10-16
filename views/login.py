from flask import Blueprint, session, request, abort
from functools import wraps

login_bp = Blueprint("login", __name__)

# use blueprint as app
@login_bp.route("/")
def database_index():
    return "Database Index"
