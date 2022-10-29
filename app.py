from flask import Flask
from flask_cors import CORS
from views.database import database_bp
from views.user import user_bp
from views.info import info_bp

app = Flask(__name__)
app.register_blueprint(database_bp, url_prefix="/database")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(info_bp, url_prefix="/info")

app.config["SECRET_KEY"] = "secret!qwq"
CORS(app, supports_credentials=True)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)