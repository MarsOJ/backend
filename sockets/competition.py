from sockets import socketio
from flask import request, session, jsonify
from views.account import login_required
from sockets import socketio, scheduler
import os
import uuid
import time
import datetime
import threading

socket_pool = dict() # dict - key:sid, value:socketData()
waiting_pool = list() # list of sid 
competing_pool = dict() # dict - key:uuid4, value:competingData()

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

    def problem_response(self, problem_id=None):
        response_form = {
            # 'problemId': problem_id
            'content':'test_content:{}'.format(uuid.uuid4())
        }
        # TODO: problem contents
        print('emit problem')
        socketio.emit("problem", response_form, to=self.sid, namespace="/competition")
        
class competingData():
    def __init__(self, sid1, sid2):
        self.userdata = {}
        self.userdata[sid1] = {'answers':[], 'score':0}
        self.userdata[sid2] = {'answers':[], 'score':0}
        self.problems = [] # TODO: get_problems()
        self.answers = []
        self.state = -1 # -1 for not start, >= 0 for problem_id
        self.timer = None
        self.mutex = threading.Lock()

@socketio.on("connect", namespace="/competition")
def on_connect():
    print("receive connect")
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
            socket_pool[sid] = data

            opponent_sid = waiting_pool.pop(0)
            socket_pool[opponent_sid].state = 1
            socket_pool[opponent_sid].opponent = sid

            socket_pool[sid].state = 1
            socket_pool[sid].opponent = opponent_sid

            competing_data_hash = str(uuid.uuid4())
            competing_data = competingData(sid, opponent_sid)
            competing_pool[competing_data_hash] = competing_data

            socket_pool[sid].competing_hash = competing_data_hash
            socket_pool[opponent_sid].competing_hash = competing_data_hash


            socket_pool[sid].prepare_response()
            socket_pool[opponent_sid].prepare_response()
    except Exception as e:
        print(e)
        pass # TODO

@socketio.on("cancel", namespace="/competition")
def on_cancel():
    print("receive cancel")
    try:
        if request.sid in waiting_pool:
            waiting_pool.remove(request.sid)
        else:
            raise('Error')
    except:
        pass

def competition_settle(competing_hash):
    pass
    # TODO:{problems:,'user1':{'score','answers',},'user2':{xx}, answers:[]}

# def check_answer(competing_hash): 
#     pass
#     # TODO: {problem:,'user1':,'user2':,answer:}

def get_next(competing_hash):
    pass
    # TODO:

def on_receive_answer(competing_hash, result_sid_list, next_flag=False):
    competing_data = competing_pool[competing_hash]

    sid1 = competing_data.sid1
    sid2 = competing_data.sid2
    scheduler.remove_job(job_id=competing_hash)

    answer_result = {} #TODO:（包括选手序号、正误、分数、是计时到了还是答题结束）
    socketio.emit("answer", answer_result, to=sid1, namespace="/competition")
    socketio.emit("answer", answer_result, to=sid2, namespace="/competition")

    if next_flag:
        time.sleep(3)
        competing_data.state += 1
        if competing_data.state >= len(competing_data.problems):
            result = competition_settle(competing_hash)
            socketio.emit("result", result, to=sid1, namespace="/competition")
            socketio.emit("result", result, to=sid2, namespace="/competition")
            del competing_pool[competing_hash]
            del socket_pool[sid1]
            del socket_pool[sid2]
            return
        
        next_data = get_next(competing_hash)
        socketio.emit("problem", next_data, to=sid1, namespace="/competition")
        socketio.emit("problem", next_data, to=sid2, namespace="/competition")

        scheduler.add_job(func=on_timer, args=(competing_hash, competing_data.state), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)

def on_timer(competing_hash, problem_id):
    competing_data = competing_pool[competing_hash]
    
    # acquire mutex lock
    competing_data.mutex.acquire()

    if problem_id == competing_data.problems[competing_data.state]:
        result_sid_list = []
        for sid in competing_data.userdata:
            if len(competing_data.userdata[sid]['answers']) == competing_data.state:
                competing_data.userdata[sid]['answers'].append(0) #TODO
                result_sid_list.append(sid)
        on_receive_answer(competing_hash, result_sid_list, True)

    # release mutex lock
    competing_data.mutex.release()
        

@socketio.on("finish", namespace="/competition")
def on_finish(problem_id, answer):
    # scoring users
    sid = request.sid
    competing_hash = socket_pool[sid].competing_hash
    competing_data = competing_pool[competing_hash]

    # acquire mutex lock
    competing_data.mutex.acquire()

    opponent_sid = socket_pool[sid].opponent
    if len(competing_data.userdata[sid]['answers']) == competing_data.state:
        competing_data.userdata[sid]['answers'].append(answer)

        if answer == competing_data.answers[competing_data.state]:
            score = (scheduler.get_job(job_id=competing_hash).next_run_time - datetime.datetime.now()).milliseconds
            competing_data.userdata[sid]['score'] += score

        next_flag =  len(competing_data.userdata[opponent_sid]['answers']) == competing_data.state + 1
        on_receive_answer(competing_hash, [sid,], next_flag)  

    # release mutex lock
    competing_data.mutex.release()

@socketio.on("start", namespace="/competition")
def on_start():
    print('receive start')
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

            # TODO: create paper
            scheduler.add_job(func=on_timer, args=(competing_hash, 0), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)
            socket_pool[sid].problem_response(0)
            socket_pool[opponent_sid].problem_response(0)
    except Exception as e:
        print(e)
        pass
