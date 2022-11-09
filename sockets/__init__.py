from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")
from views.account import login_required


from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

from . import competition