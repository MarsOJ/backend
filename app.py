from flask import Flask
from flask_cors import CORS
from views.database import database_bp
from views.account import account_bp
from views.info import info_bp,question_bp
from sockets import socketio

app = Flask(__name__)
app.register_blueprint(database_bp, url_prefix="/database")
app.register_blueprint(account_bp, url_prefix="/account")
app.register_blueprint(info_bp, url_prefix="/info")
app.register_blueprint(question_bp, url_prefix="/question")

app.config["SECRET_KEY"] = "secret!qwq"

socketio.init_app(app)
# app.config['DEBUG'] = True


CORS(app, supports_credentials=True)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)