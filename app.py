from flask import Flask
from flask_cors import CORS
from views.database import database_bp
from views.account import account_bp
from views.info import info_bp
from views.question import question_bp
from views.favorite import favorite_bp
from views.record import record_bp
from sockets import socketio
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger

app = Flask(__name__)

swagger = Swagger(app)
# SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
# API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)
# # Call factory function to create our blueprint
# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
#     API_URL,
#     config={  # Swagger UI config overrides
#         'app_name': "Test application"
#     },
#     # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
#     #    'clientId': "your-client-id",
#     #    'clientSecret': "your-client-secret-if-required",
#     #    'realm': "your-realms",
#     #    'appName': "your-app-name",
#     #    'scopeSeparator': " ",
#     #    'additionalQueryStringParams': {'test': "hello"}
#     # }
# )
# app.register_blueprint(swaggerui_blueprint)


app.register_blueprint(database_bp, url_prefix="/database")
app.register_blueprint(account_bp, url_prefix="/account")
app.register_blueprint(info_bp, url_prefix="/info")
app.register_blueprint(question_bp, url_prefix="/question")
app.register_blueprint(favorite_bp, url_prefix="/favorite")
app.register_blueprint(record_bp, url_prefix="/record")


app.config["SECRET_KEY"] = "secret!qwq"

socketio.init_app(app)
# app.config['DEBUG'] = True


CORS(app, supports_credentials=True)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route('/register/', methods=['POST'])
# def register():
#     """
#     用户注册
#     ---
#     tags:
#       - 用户相关接口
#     description:
#         用户注册接口，json格式
#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           id: 用户注册
#           required:
#             - username
#             - password
#             - inn_name
#           properties:
#             username:
#               type: string
#               description: 用户名.
#             password:
#               type: string
#               description: 密码.
#             inn_name:
#               type: string
#               description: 客栈名称.
#             phone:
#               type: string
#               description: 手机号.
#             wx:
#               type: string
#               description: 微信.

#     responses:
#       201:
#           description: 注册成功


#           example: {'code':1,'message':注册成功}
#       406:
#         description: 注册有误，参数有误等

#     """
#     pass


if __name__ == "__main__":
    app.run(debug=True)