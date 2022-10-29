from flask import Blueprint, session, request, abort
from functools import wraps
import json

# use blueprint as app
user_bp = Blueprint("user", __name__)

@user_bp.route("/")
def user_index():
    return "User Index"

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        if 'username' not in session:
            abort(401)
        return func(args, kargs)
    return wrapper


@user_bp.route("/login", methods=['POST'])
def login():
    data = json.loads(request.data)
    try:
        username = data['username']
        password = data['password']
    except:
        return "Post request invalid", 400
    if True:
        # TODO: connect database
        session['username'] = username
        return "success", 200
    return "Username/Password error", 400

@user_bp.route("/logout", methods=['POST'])
@login_required
def logout():
    session.pop('username', None)
    return "success", 200

@user_bp.route("/login_check", methods=['GET'])
@login_required
def check_login_state():
    return session['username'], 200

