from flask import Flask
from flask_cors import CORS
from views.database import database_bp
from views.account import account_bp
from views.info import info_bp
from views.question import question_bp
from views.favorite import favorite_bp
from views.record import record_bp
from sockets import socketio



app = Flask(__name__)

try:
    from flask_swagger_ui import get_swaggerui_blueprint
    from flasgger import Swagger
    swagger = Swagger(app)
except Exception as e:
    print(e)



app.register_blueprint(database_bp, url_prefix="/database")
app.register_blueprint(account_bp, url_prefix="/account")
app.register_blueprint(info_bp, url_prefix="/info")
app.register_blueprint(question_bp, url_prefix="/question")
app.register_blueprint(favorite_bp, url_prefix="/favorite")
app.register_blueprint(record_bp, url_prefix="/record")


app.config["SECRET_KEY"] = "secret!qwq"

socketio.init_app(app)

CORS(app, supports_credentials=True)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"




if __name__ == "__main__":
    app.run(debug=True)