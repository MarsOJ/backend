from sockets import socketio
from flask import request, session, jsonify
from views.account import login_required
from sockets import socketio, scheduler
import os
import uuid
import time
import datetime
import threading
from views.database import *
import copy
import json

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

    def prepare_response(self, competitor_list):
        # response_form = [socket_pool[self.opponent].username]
        socketio.emit("prepare", competitor_list, to=self.sid, namespace="/competition")

    def problem_response(self, problem_id=None, problem=None):
        try:
            res = {
                'problemID': problem_id,
                'content': problem['content'],
                'type': problem['classification'],
                'time': 30, # TODO: to be precise
                'subproblem':problem['subproblem'],
            }
            socketio.emit("problem", res, to=self.sid, namespace="/competition")
            print('emit problem')
        except Exception as e:
            print(e)
        
class competingData():
    def __init__(self, sid1, sid2):
        self.userdata = {}
        self.userdata[sid1] = {'answer':[], 'score':0, 'score_list':[], 'alive':True}
        self.userdata[sid2] = {'answer':[], 'score':0, 'score_list':[], 'alive':True}
        self.problems = []
        self.state = -1 # -1 for not start, >= 0 for problem_id
        self.timer = None
        self.mutex = threading.Lock()

@socketio.on("pair", namespace="/competition")
def on_connect():
    print("receive pair")
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

            competitor_list = [socket_pool[temp_sid].username for temp_sid in competing_data.userdata.keys()]
            socket_pool[sid].prepare_response(competitor_list)
            socket_pool[opponent_sid].prepare_response(competitor_list)
            print(sid)
            print(opponent_sid)
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

def to_problem(competing_hash):
    competing_data = competing_pool[competing_hash]
    competing_data.mutex.acquire()
    for sid in competing_data.userdata.keys():
            socket_pool[sid].problem_response(competing_data.state, competing_pool[competing_hash].problems[competing_data.state])
    scheduler.add_job(func=on_timer, args=(competing_hash, competing_data.state), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)

    competing_data.mutex.release()

def to_next(competing_hash):
    scheduler.remove_job(job_id=competing_hash)
    competing_data = competing_pool[competing_hash]
    competing_data.state += 1
    
    lastQuestion = competing_data.state >= len(competing_data.problems) 
    next_data = {
            'answer':competing_data.problems[competing_data.state - 1]['answer'],
            'lastQuestion':lastQuestion,
        }
    for sid in competing_data.userdata.keys():
        socketio.emit("next", next_data, to=sid, namespace="/competition")
    
    if lastQuestion:
        return
    else:
        s = threading.Timer(3, to_problem, (competing_hash))
        s.start()
        

def on_timer(competing_hash, problem_id):
    competing_data = competing_pool[competing_hash]
    
    # acquire mutex lock
    competing_data.mutex.acquire()
    print(len(competing_data.problems))
    if problem_id == competing_data.state and problem_id < len(competing_data.problems):
        result_sid_list = []
        for sid in competing_data.userdata.keys():
            if len(competing_data.userdata[sid]['answer']) == competing_data.state:
                competing_data.userdata[sid]['answer'].append([False]*len(competing_data.problems[problem_id]['answer']))
                competing_data.userdata[sid]['score_list'].append([0]*len(competing_data.problems[problem_id]['answer']))
        to_next(competing_hash)

    # release mutex lock
    competing_data.mutex.release()
        

@socketio.on("finish", namespace="/competition")
def on_finish(problem_id, answer):
    print("receive finish")
    # scoring users
    sid = request.sid
    competing_hash = socket_pool[sid].competing_hash
    username = socket_pool[sid].username
    competing_data = competing_pool[competing_hash]

    # acquire mutex lock
    competing_data.mutex.acquire()

    opponent_sid = socket_pool[sid].opponent
    if len(competing_data.userdata[sid]['answer']) == competing_data.state:
        competing_data.userdata[sid]['answer'].append(answer)

        correct = []
        score_list = []
        for i in range(len(answer)):
            print(answer)
            print(competing_data.problems[competing_data.state]['answer'])
            if answer[i] == competing_data.problems[competing_data.state]['answer'][i]:
                correct.append(True)
                score = (scheduler.get_job(job_id=competing_hash).next_run_time.replace(tzinfo=None) - datetime.datetime.now()).seconds + 10
                competing_data.userdata[sid]['score'] += score
                score_list.append(score)
            else:
                correct.append(False)
                score_list.append(0)
        
        competing_data.userdata[sid]['score_list'].append(score_list)
        print(competing_data.userdata[sid]['score_list'])
        
        # whether it's the last problem
        # print(competing_data.userdata[opponent_sid]['answer'], competing_data.state)
        next_flag =  len(competing_data.userdata[opponent_sid]['answer']) == competing_data.state + 1
        
        ret_form = {
            'username':username,
            'correct':correct,
            'score':competing_data.userdata[sid]['score'],
        }
        for sid in competing_data.userdata.keys():
            socketio.emit("answer", ret_form, to=sid, namespace="/competition")    

        if next_flag:
            to_next(competing_hash)


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

            competing_pool[competing_hash].problems = db_get_random_questions()

            scheduler.add_job(func=on_timer, args=(competing_hash, 0), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)
            print("in problem response")
            socket_pool[sid].problem_response(0, competing_pool[competing_hash].problems[0])
            socket_pool[opponent_sid].problem_response(0, competing_pool[competing_hash].problems[0])
    except Exception as e:
        print(e)
        pass

@socketio.on("result", namespace="/competition")
def on_result():
    this_sid = request.sid
    competing_hash = socket_pool[this_sid].competing_hash
    username = socket_pool[this_sid].username
    competing_data = competing_pool[competing_hash]
    result = {'points':[], 'problems':[]}
    points = [[] for _ in range(len(competing_data.problems))] 
    for sid in competing_data.userdata.keys():
        result['points'].append({'name':socket_pool[sid].username, 'points':competing_data.userdata[sid]['score']})
        for i, score_list in enumerate(competing_data.userdata[sid]['score_list']):
            # print(points)
            # print(points[1], i)
            points[i].append(score_list)
            # print(points)
            # print(points[1], i)
    for i, problem in enumerate(competing_data.problems):
        result['problems'].append({
            'num':i,
            'id':str(problem['_id']),
            'type':problem['classification'],
            'points':points[i],
        })
    print(result['problems'])
    # for sid in competing_data.userdata.keys():
    socketio.emit("result", result, to=this_sid, namespace="/competition")
    competing_data.userdata[this_sid]['alive'] = False
    # del socket_pool[this_sid]

    clear_competing_hash = True
    for sid in competing_data.userdata.keys():
        if competing_data.userdata[sid]['alive']:
            clear_competing_hash = False
            break
    if clear_competing_hash:
        for sid in competing_data.userdata.keys():
            del socket_pool[sid]
        del competing_pool[competing_hash]

@socketio.on("disconnect", namespace="/competition")
def on_disconnect():
    pass