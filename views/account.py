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
    """
    用户登录
    ---
    tags:
      - 用户账号
    description:
        用户登录接口,json格式,注册成功返回username,200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: password
        type: string
        required: true
        description: 密码
    responses:
      200:
          description: OK,return username,200
      400:
        description: Username/Password Error
    """
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
    """
    用户登出
    ---
    tags:
      - 用户账号
    description:
        用户登出接口,session中删除username字段
    responses:
      200:
          description: OK,return "Success", 200
    """
    session.pop('username', None)
    return "Success", 200

@account_bp.route("/state/", methods=['GET'])
def check_login_state():
    """
    用户登入状态查看
    ---
    tags:
      - 用户账号
    description:
        用户登入状态查看接口，查看session中是否有username字段
    responses:
      200:
          description: OK,return username,200
      400:
        description: return "Not Logged In", 400
    """
    if 'username' in session:
        return session['username'], 200    
    return "Not Logged In", 400

@account_bp.route("/register/", methods=['POST'])
def register():
    """
    用户注册
    ---
    tags:
      - 用户账号
    description:
        用户注册接口,json格式,用户名不能与数据库内重复，注册成功返回"Success", 200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: password
        type: string
        required: true
        description: 密码
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: Username/Password Error,return "Repeated Username", 400 或 "Bad Request", 400或"Register Error", 400
    """
    try:
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        # print('/account/register/')
        res = db_select_user(username)
        if res is False:
            return "Register Error", 400
        # print('res1 /account/register/')
        if res is not None:
            return "Repeated Username", 400
        # print('res2 /account/register/')
        if not db_insert_user(username, password):
            return "Register Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400

@account_bp.route("/delete/", methods=['DELETE'])
def delete():
    """
    用户账户删除
    ---
    tags:
      - 用户账号
    description:
        用户账户删除接口,json格式,删除成功返回"Success", 200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: password
        type: string
        required: true
        description: 密码
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: Username/Password Error,return "Username/Password Error", 400 或 "Delete User Error", 400或"Bad Request", 400
    """

    try:
        data = json.loads(request.data)

        # MODIFIED
        username = data['username']
        password = data['password']
        print('/account/delete/: 1')
        if not db_verify_user(username, password):
            return "Username/Password Error", 400
        print('/account/delete/: 2')
        if not db_delete_user(username):
            return "Delete User Error", 400
        return "Success", 200
    except:
        return "Bad Request", 400

@account_bp.route("/change-password/", methods=['POST'])
@login_required
def change_password():
    """
    用户账户密码修改，需要已登录状态
    ---
    tags:
      - 用户账号
    description:
        用户账户密码修改接口,json格式,修改成功返回"Success", 200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: password
        type: string
        required: true
        description: 密码
      - name: newPassword
        type: string
        required: true
        description: 新的密码
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: Username/Password Error return "Username/Password Error", 400 或 "Change Password Error", 400或"Bad Request", 400
    """

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
    """
    用户信息查看，需要已登录状态
    ---
    tags:
      - 用户账号
    description:
        用户信息查看接口,获取基本信息：用户名、总积分、参与场次、pk胜场次、答题次数、正确题数、等级、是否为管理员、个人签名,url的args输入,返回json, 200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
    responses:
      200:
        description: OK,return "Success", 200
        schema:
          id: User
          properties:
            username:
              type: string
              description: The name of the user
            credit:
              type: int
              description: 积分
            totalCompetitionsNum:
              type: int
            victoriesNum:
              type: int
            totalAnswersNum:
              type: int
            correctAnswersNum:
              type: int
            authority:
              type: bool
            slogan:
              type: string
            profile:
              type: string            
      400:
        description: Username/Password Error return str(erro_description), 400
    """
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
    """
    用户上传post/获取get头像，需要已登录状态
    ---
    tags:
      - 用户账号
    description:
        用户上传post/获取get头像接口,json格式,return 图片base64,200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: profile
        type: string
        description: 头像，post时必须，get无需
    responses:
      200:
        description: OK,return "Success", 200/return 图片base64,200
      400:
        description: Username/Password Error return  "Database Error", 400
    """
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
    """
    用户修改签名，需要已登录状态
    ---
    tags:
      - 用户账号
    description:
        用户修改签名接口,json格式,修改成功返回"Success", 200
    parameters:
      - name: username
        type: string
        required: true
        description: 用户名
      - name: signature
        type: string
        required: true
        description: 签名
    responses:
      200:
          description: OK,return "Success", 200
      400:
        description: Username/Password Error return "Database Error", 400
    """
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
