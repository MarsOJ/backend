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

def authority_required(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        if 'username' not in session:
            abort(401)
        username = session['username']
        user_info = db_select_user(username)
        if not user_info['authority']:
            raise Exception('Authority Error')
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
    print(username, password)
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
        username = session['username']
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
        username = session['username']
        password = data['password']
        newpw = data['newPassword']
        
        if not db_verify_user(username, password):
            return "Username/Password Error", 400
        if not db_update_user(username, newpw):
            return "Change Password Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400


@account_bp.route("/info/", methods=['GET'])
@login_required
def get_info():
    try:
        try:
            username = str(request.args.get('username'))
        except:
            username = session['username']
        info = db_select_user(username)
        del info['pwhash']
        del info['favorite']
        if not info:
            raise Exception('Database Error')
        return json.dumps(info), 200
    except Exception as e:
        print(e)
        return str(e), 400

@account_bp.route("/profile/", methods=['GET', 'POST'])
@login_required
def profile():
    try:
        
        if (request.method == 'POST'):
            name = session['username']
            data = json.loads(request.data)
            profile = data['profile']
            _, state = db_update_profile(name, profile)
            if not state:
                return "Database Error", 400
            return "Success", 200
        else:
            try:
                username = str(request.args.get('username'))
            except:
                username = session['username']
            print(username)
            _, state = db_select_profile(username)
            if not state:
                return "Database Error", 400
            return _, 200
    except Exception as e:
        return str(e), 400

@account_bp.route("/signature/", methods=['POST'])
@login_required
def signature():
    try:
        name = session['username']
        data = json.loads(request.data)
        signature = data['signature']
        _, state = db_update_signature(name, signature)
        if not state:
            return "Database Error", 400
        return "Success", 200
       
    except Exception as e:
        return str(e), 400
