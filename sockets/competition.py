from sockets import socketio
from flask import request, session, jsonify
from views.account import login_required
from sockets import socketio, scheduler
import os
import uuid

socket_pool = dict() # dict
waiting_pool = list() # list of sid 
competing_pool = dict()

class socketData():
    def __init__(self, sid, username, state):
        self.sid = sid
        self.username = username
        self.state = state # 0 for waiting, 1 for preparing, 2 for started(but opponent didn't), 3 for competing
        self.opponent = None # sid
        self.competing_hash = None

    def prepare_response(self):
        response_form = {
            'opponent' : socket_pool[self.opponent].username
        }
        socketio.emit("prepare", response_form, to=self.sid, namespace="/competition")
    def problem_response(self, problem_id):
        response_form = {
            'problemId': problem_id
        }
        # TODO: problem contents
        socketio.emit("problem", response_form, to=self.sid, namespace="/competition")
        
class competingData():
    def __init__(self, sid1, sid2):
        self.sid1 = sid1
        self.sid2 = sid2
        self.problems = [] # TODO: get_problems()
        self.answer1 = []
        self.answer2 = []
        self.score1 = 0
        self.score2 = 0
        self.state = -1 # -1 for not start, >= 0 for problem_id
        self.timer = None

@socketio.on("connect", namespace="/competition")
def on_connect():
    try:
        # if there is no waiting users
        if len(waiting_pool)== 0:
            username = session['username']
            state = 0
            data = socketData(request.sid, username, state)
            waiting_pool.append(request.sid)
            socket_pool[request.sid] = data
        else:
            username = session['username']
            state = 1
            sid = request.sid
            data = socketData(request.sid, username, state)

            opponent_sid = waiting_pool.pop(0)
            socket_pool[opponent_sid].state = 1
            socket_pool[opponent_sid].opponent = sid

            socket_pool[sid].state = 1
            socket_pool[sid].opponent = opponent_sid

            competing_data_hash = uuid.uuid4()
            competing_data = competingData(sid, opponent_sid)
            competing_pool[competing_data_hash] = competing_data

            socket_pool[sid].competing_hash = competing_data_hash
            socket_pool[opponent_sid].competing_hash = competing_data_hash

            socket_pool[sid].prepare_response()
            socket_pool[opponent_sid].prepare_response()
    except:
        pass # TODO

@socketio.on("cancel", namespace="/competition")
def on_cancel():
    try:
        if request.sid in waiting_pool:
            waiting_pool.remove(request.sid)
        else:
            raise('Error')
    except:
        pass

def on_timer(competing_hash, problem_id):
    scheduler.remove_job(job_id=competing_hash)
    #TODO

@socketio.on("finish", namespace="/competition")
def on_finish():
    #TODO
    pass


@socketio.on("start", namespace="/competition")
def on_start():
    try:
        sid = request.sid
        opponent_sid = socket_pool[sid].opponent
        competing_hash = socket_pool[sid].competing_hash
        if socket_pool[sid].state == 2:
            return
        if socket_pool[sid].state == 1 and socket_pool[opponent_sid].state == 1:
            socket_pool[sid].state = 2
            competing_pool[competing_hash].state = -1
        elif socket_pool[sid].state == 1 and socket_pool[opponent_sid].state == 2:
            socket_pool[sid].state = 3
            socket_pool[opponent_sid].state = 3
            competing_pool[competing_hash].state = 0


            scheduler.add_job(func=on_timer, args=(competing_hash, 0), id=competing_hash, trigger='interval',seconds=30, replace_existing=True)
            socket_pool[sid].prepare_response(0)
            socket_pool[opponent_sid].prepare_response(0)


    except:
        pass