from flask import Blueprint, session, request, abort
from views.database import *
from functools import wraps
import json

# use blueprint as app
account_bp = Blueprint("account", __name__)

@account_bp.route("/")
def user_index():
    return "Account Index"

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        if 'username' not in session:
            abort(401)
        return func(*args, **kargs)
    return wrapper

@account_bp.route("/login/", methods=['POST'])
def login():
    data = json.loads(request.data)
    try:
        username = data['username']
        password = data['password']
    except:
        return "Bad Request", 400
    if db_verify_user(username, password):
        session['username'] = username
        return username, 200
    return "Username/Password Error", 400

@account_bp.route("/logout/", methods=['POST'])
def logout():
    session.pop('username', None)
    return "Success", 200

@account_bp.route("/state/", methods=['GET'])
def check_login_state():
    if 'username' in session:
        return session['username'], 200    
    return "Not Logged In", 400

@account_bp.route("/register/", methods=['POST'])
def register():
    try:
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        res = db_select_user(username)
        if res is False:
            return "Register Error", 400
        if res is not None:
            return "Repeated Username", 400
        if not db_insert_user(username, password):
            return "Register Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400

@account_bp.route("/delete/", methods=['DELETE'])
def delete():
    try:
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        if not db_verify_user(username, password):
            return "Username/Password Error", 400
        if not db_delete_user(username):
            return "Delete User Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400

@account_bp.route("/change-password/", methods=['POST'])
@login_required
def change_password():
    try:
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        newpw = data['newPassword']
        
        if not db_verify_user(username, password):
            return "Username/Password Error", 400
        if not db_update_user(username, newpw):
            return "Change Password Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400
