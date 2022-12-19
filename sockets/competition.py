from sockets import socketio
from flask import request, session, jsonify
from views.account import login_required
from sockets import socketio, scheduler
from functools import reduce
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

global_mutex = threading.Lock()
PLAYER_NUM = 2

class socketData():
    def __init__(self, sid, username, state):
        self.sid = sid
        self.username = username
        self.state = state # 0 for waiting, 1 for preparing, 2 for started(but opponent didn't), 3 for competing
        self.competing_hash = None

    def prepare_response(self, competitor_list):
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
    def __init__(self, sid_list):
        self.sidlist = sid_list
        self.userdata = {sid: {'answer':[], 'score':0, 'score_list':[], 'alive':True} for sid in sid_list}
        self.problems = []
        self.state = -1 # -1 for not start, >= 0 for problem_id
        self.timer = None
        self.mutex = threading.Lock()

# TODO
@socketio.on("pair", namespace="/competition")
def on_connect():
    print("receive pair")
    global global_mutex, waiting_pool, socket_pool, competing_pool
    global_mutex.acquire()
    try:
        # if there is no waiting users
        if len(waiting_pool) < PLAYER_NUM - 1:
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

            sid_list = [sid]
            print(waiting_pool[:PLAYER_NUM - 1])
            sid_list.extend(waiting_pool[:PLAYER_NUM - 1])
            waiting_pool = waiting_pool[PLAYER_NUM - 1:]

            competing_data_hash = str(uuid.uuid4())
            competing_data = competingData(sid_list)
            competing_pool[competing_data_hash] = competing_data
            competitor_list = [socket_pool[temp_sid].username for temp_sid in sid_list]

            for sid in sid_list:
                socket_pool[sid].state = 1
                socket_pool[sid].competing_hash = competing_data_hash
                socket_pool[sid].prepare_response(competitor_list)
        
    except Exception as e:
        print(e)
        pass # TODO
    global_mutex.release()

@socketio.on("cancel", namespace="/competition")
def on_cancel():
    print("receive cancel")
    global waiting_pool
    try:
        if request.sid in waiting_pool:
            waiting_pool.remove(request.sid)
        else:
            raise Exception('Error')
    except:
        pass

def to_problem(competing_hash):
    global waiting_pool, socket_pool, competing_pool
    competing_data = competing_pool[competing_hash]
    competing_data.mutex.acquire()
    for sid in competing_data.sidlist:
            socket_pool[sid].problem_response(competing_data.state, competing_pool[competing_hash].problems[competing_data.state])
    scheduler.add_job(func=on_timer, args=(competing_hash, competing_data.state), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)

    competing_data.mutex.release()

def to_next(competing_hash):
    global waiting_pool, socket_pool, competing_pool
    scheduler.remove_job(job_id=competing_hash)
    competing_data = competing_pool[competing_hash]
    competing_data.state += 1
    
    lastQuestion = competing_data.state >= len(competing_data.problems) 
    next_data = {
            'answer':competing_data.problems[competing_data.state - 1]['answer'],
            'lastQuestion':lastQuestion,
        }
    for sid in competing_data.sidlist:
        socketio.emit("next", next_data, to=sid, namespace="/competition")
    
    if lastQuestion:
        return
    else:
        s = threading.Timer(3, to_problem, (competing_hash,))
        s.start()
        

def on_timer(competing_hash, problem_id):
    global waiting_pool, socket_pool, competing_pool
    competing_data = competing_pool[competing_hash]
    
    # acquire mutex lock
    competing_data.mutex.acquire()
    print(len(competing_data.problems))
    if problem_id == competing_data.state and problem_id < len(competing_data.problems):
        result_sid_list = []
        for sid in competing_data.sidlist:
            if len(competing_data.userdata[sid]['answer']) == competing_data.state:
                competing_data.userdata[sid]['answer'].append([False]*len(competing_data.problems[problem_id]['answer']))
                competing_data.userdata[sid]['score_list'].append([0]*len(competing_data.problems[problem_id]['answer']))
        to_next(competing_hash)

    # release mutex lock
    competing_data.mutex.release()
        
# TODO:
@socketio.on("finish", namespace="/competition")
def on_finish(problem_id, answer):
    print("receive finish")
    global waiting_pool, socket_pool, competing_pool
    # scoring users
    sid = request.sid
    competing_hash = socket_pool[sid].competing_hash
    username = socket_pool[sid].username
    competing_data = competing_pool[competing_hash]
    sid_list = competing_data.sidlist

    # acquire mutex lock
    competing_data.mutex.acquire()
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
        next_flag = True
        for t_sid in sid_list:
            if len(competing_data.userdata[t_sid]['answer']) != competing_data.state + 1:
                next_flag = False
        
        ret_form = {
            'username':username,
            'correct':correct,
            'score':competing_data.userdata[sid]['score'],
        }
        for sid in competing_data.sidlist:
            socketio.emit("answer", ret_form, to=sid, namespace="/competition")    

        if next_flag:
            to_next(competing_hash)


    # release mutex lock
    competing_data.mutex.release()

@socketio.on("start", namespace="/competition")
def on_start():
    print('receive start')
    global waiting_pool, socket_pool, competing_pool
    competing_data = None
    try:
        sid = request.sid
        competing_hash = socket_pool[sid].competing_hash
        competing_data = competing_pool[competing_hash]
        competing_data.mutex.acquire()
        if socket_pool[sid].state == 2:
            competing_data.mutex.release()
            return

        # check if others are all ready
        other_ready = True
        for t_sid in competing_data.sidlist:
            if socket_pool[t_sid].state != 2 and t_sid != sid:
                other_ready = False
        print(other_ready)
        if socket_pool[sid].state == 1 and not other_ready:
            socket_pool[sid].state = 2
            competing_pool[competing_hash].state = -1
        elif socket_pool[sid].state == 1 and other_ready:
            competing_pool[competing_hash].state = 0
            competing_pool[competing_hash].problems = db_get_random_questions()
            
            scheduler.add_job(func=on_timer, args=(competing_hash, 0), id=competing_hash, trigger='interval',seconds=30, replace_existing=True, max_instances=1)
            # TODO: ERROR PROCESSING
            print("in problem response")
            for t_sid in competing_data.sidlist:
                
                socket_pool[t_sid].state = 3
                socket_pool[t_sid].problem_response(0, competing_pool[competing_hash].problems[0])
        
    except Exception as e:
        print(e)
    if (competing_data): 
        competing_data.mutex.release()

def settlement(username_list, points, problem_set):
    scores = [[] for _ in range(len(username_list))] # scores[i][j] means player i got how much scores in problem j
    correctness = [[] for _ in range(len(username_list))]
    for point in points:
        for idx in range(len(username_list)):
            scores[idx].append(sum(point[idx]))
            correctness[idx].append(reduce(lambda x, y : x and y, list(map(lambda x : x > 0, point[idx]))))
    total_problems = len(points)

    ranklist = [{'username':username_list[i], 'correctness':correctness[i], 'score':scores[i]} for i in range(len(username_list))]

    ranklist.sort(key=lambda x:sum(x['score']), reverse=True)
    credit = len(ranklist) - 1
    for idx, rank in enumerate(ranklist):
        username = rank['username']
        if (idx == 0 or sum(rank['score']) == sum(ranklist[idx - 1]['score'])):
            pass
        else:
            credit = len(ranklist) - idx - 1
        correctAnswersNum = sum(rank['correctness'])
        totalAnswersNum = total_problems
        victoriesNum = 1 if credit == len(ranklist) - 1 else 0
        db_competition_settlement_user(username, credit, correctAnswersNum, totalAnswersNum, victoriesNum)
    
    problem_id = [str(problem['_id']) for problem in problem_set]
    db_competition_settlement_result(problem_id ,ranklist)

@socketio.on("result", namespace="/competition")
def on_result():
    global waiting_pool, socket_pool, competing_pool
    this_sid = request.sid
    competing_hash = socket_pool[this_sid].competing_hash
    username = socket_pool[this_sid].username
    competing_data = competing_pool[competing_hash]
    result = {'points':[], 'problems':[]}
    points = [[] for _ in range(len(competing_data.problems))] 
    for sid in competing_data.sidlist:
        result['points'].append({'name':socket_pool[sid].username, 'points':competing_data.userdata[sid]['score']})
        for i, score_list in enumerate(competing_data.userdata[sid]['score_list']):
            points[i].append(score_list)
    for i, problem in enumerate(competing_data.problems):
        result['problems'].append({
            'num':i,
            'id':str(problem['_id']),
            'type':problem['classification'],
            'points':points[i],
        })
    print(result['problems'])
    socketio.emit("result", result, to=this_sid, namespace="/competition")
    competing_data.userdata[this_sid]['alive'] = False

    clear_competing_hash = True
    for sid in competing_data.sidlist:
        if competing_data.userdata[sid]['alive']:
            clear_competing_hash = False
            break
    if clear_competing_hash:
        username_list = [socket_pool[sid].username for sid in competing_data.sidlist]
        settlement(username_list, points, competing_data.problems)
        for sid in competing_data.sidlist:
            del socket_pool[sid]
        del competing_pool[competing_hash]

@socketio.on("disconnect", namespace="/competition")
def on_disconnect():
    global waiting_pool, socket_pool, competing_pool
    pass