from flask import Blueprint, Flask, request, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv, find_dotenv
import os
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import uuid

database_bp = Blueprint("database", __name__)

load_dotenv(dotenv_path=r'../', verbose=True)
DB_URL = os.getenv('FLASK_APP_DB_URL')
client = pymongo.MongoClient(DB_URL)
db = client["MarsOJ"]

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"

def db_competition_settlement_user(username, credit, correctAnswersNum, totalAnswersNum, victoriesNum):
    try:
        collection = db["account"]
        select_res = db_select_user(username)

        select_res['credit'] += credit
        select_res['correctAnswersNum'] += correctAnswersNum
        select_res['totalAnswersNum'] += totalAnswersNum
        select_res['victoriesNum'] += victoriesNum
        select_res['totalCompetitionsNum'] += 1
        update_res = collection.update_one({'username':username}, {'$set':select_res})
        if update_res.modified_count != 1:
            return 'Update error', False
        return 'success', True
    except Exception as e:
        print(e)
        return str(e), False

def db_competition_settlement_result(problemID, userResult):
    try:
        collection = db["record"]
        insert_content = {
            'problemID':problemID,
            'userResult':userResult, # [{'username':, 'correctness':[], 'score':[]}, ...]
            'userList':[i['username'] for i in userResult],
            'date':datetime.datetime.now()
        }
        collection.insert_one(insert_content)
        return 'success', True
    except Exception as e:
        return str(e), False

def db_select_record(_id):
    try:
        collection = db["record"]
        info_data = {
            "_id": ObjectId(_id)
        }
        return collection.find_one(info_data)
    except Exception as e:
        return False

def db_next_record(username='', _id=''):
    try:
        collection = db["record"]
        condition = {}
        if username != '':
            condition['userList'] = { '$all': [username]}
        if _id != '':
            condition['_id'] = {'$lt':ObjectId(_id)}

        find_res = collection.find(filter=condition, sort=[('_id',pymongo.DESCENDING)], limit=5)
        find_res = list(find_res)
        return find_res, True
    except Exception as e:
        return str(e), False

def db_count_record(username='', _id=''):
    try:
        collection = db["record"]
        condition = {}
        if username != '':
            condition['userList'] = { '$all': [username]}
        find_res = collection.count_documents(condition)
        return find_res, True
    except Exception as e:
        return str(e), False

def db_count_info():
    try:
        collection = db["info"]
        print('k')
        find_res = collection.count_documents({})
        print(find_res)
        return find_res, True
    except Exception as e:
        return str(e), False

def db_count_problem():
    try:
        collection = db["question"]
        find_res = collection.count_documents({})
        print(find_res)
        return find_res, True
    except Exception as e:
        return str(e), False

def db_ranklist():
    try:
        collection = db["account"]
        find_res = collection.find(filter={}, sort=[('credit',pymongo.DESCENDING)], limit=10)
        find_res = list(find_res)
        return find_res, True
    except Exception as e:
        return str(e), False  

def db_select_user(name):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        res = collection.find_one(user) # return dict
        # res['_id'] = str(res['_id'])
        
        if isinstance(res, dict) and '_id' in res.keys():
            del res['_id']
        return res
    except Exception as e:
        print(e)
        return False

def db_select_userinfo(name):
    try:
        info = db_select_userinfo(name)
        return info
    except Exception as e:
        print(e)
        return False

def db_insert_user(name, pw):
    try:
        pwhash = generate_password_hash('NAME:'+name+'|PW:'+pw, method='pbkdf2:sha256', salt_length=8)
        collection = db["account"]
        user = {
            'username': name, 
            'pwhash': pwhash,
            'favorite': {'0':{'name':'默认收藏夹', 'problemID':{}}},
            'credit': 0,
            'profile': '',
            'authority': False,
            'totalAnswersNum': 0,
            'correctAnswersNum': 0,
            'totalCompetitionsNum': 0,
            'victoriesNum': 0,
            'signature':'',
        }
        collection.insert_one(user)
        return True
    except:
        return False

def db_update_signature(username, signature):
    try:
        collection = db["account"]
        update_res = collection.update_one({'username':username}, {'$set':{'signature':signature}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return 'success', True
    except Exception as e:
        return str(e), False

def db_update_profile(username, newProfile):
    try:
        collection = db["account"]
        update_res = collection.update_one({'username':username}, {'$set':{'profile':newProfile}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return 'success', True
    except Exception as e:
        return str(e), False

def db_select_profile(name):
    try:
        item = db_select_user(name)
        return item['profile'], True
    except:
        return 'Key error', False

def db_insert_favorite(username, favorite_name):
    try:
        item = db_select_user(username)
        favorites = item['favorite']
        names = [v['name'] for k,v in favorites.items()]
        if favorite_name in names:
            return 'Repeated name', False
        favoriteID = str(uuid.uuid4())
        
        favorites[favoriteID] = ({
            'name':favorite_name,
            'problemID':{}
        })
        
        collection = db["account"]
        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return 'success', True
    except Exception as e:
        return str(e), False

def db_delete_favorite_problem(username, favorite_id, problem_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        problem_set = fav['problemID']
        success_num = 0
        noexist_num = 0
        failed_num = 0
        add_items = []
        for problem in problem_id:
            print(problem)
            # check if problem in favorites
            if problem not in problem_set.keys():
                noexist_num += 1
            # check if in dataset
            # elif not db_select_questions(_id=problem):
            #     failed_num += 1
            else:
                # problem_set.remove(problem)
                del problem_set[problem]
                success_num += 1
        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            failed_num += success_num
            success_num = 0
        return (success_num, noexist_num, failed_num), True
    except Exception as e:
        print(e)
        return str(e), False

def db_move_favorite_problem(username, problem_id, dest_id, source_id, delete_tag):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        dest_fav = favorites[dest_id]
        source_fav = favorites[source_id]
        dest_problem = dest_fav['problemID']
        source_problem = source_fav['problemID']

        success_num = 0
        failed_num = 0
        for problem in problem_id:
            # check if problem in favorites
            if problem not in source_problem.keys() or problem in dest_problem.keys():
                failed_num += 1
            else:
                dest_problem[problem] = {'modified_date':datetime.datetime.now()}
                if delete_tag:
                    # source_problem.remove(problem)
                    del source_problem[problem]
                success_num += 1

        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            failed_num += success_num
            success_num = 0
        return (success_num, failed_num), True
    except:
        print('errror')
        return 'Key error', False

def db_insert_favorite_problem(username, favorite_id, problem_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        problem_set = fav['problemID']
        success_num = 0
        failed_num = 0
        repeated_num = 0
        add_items = {}
        for problem in problem_id:
            # check if problem in favorites
            if problem in problem_set.keys():
                repeated_num += 1
            # check if in dataset
            elif not db_select_questions(_id=problem):
                failed_num += 1
            else:
                # add_items.append(problem)
                add_items[problem] = {'modified_date':datetime.datetime.now()}

        problem_set.update(add_items)
        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            failed_num += len(add_items)
        else:
            success_num = len(add_items)
        return (success_num, repeated_num, failed_num), True
    except:
        return 'Key error', False

def db_select_favorite_problem(username, favorite_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        problem_set = fav['problemID']
        problem_set = [(k, v['modified_date']) for k, v in problem_set.items()]
        problem_set.sort(key = lambda x:x[1])
        return problem_set, True
    except:
        return 'Key error', False

def db_delete_favorite(username, favorite_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        del favorites[favorite_id]

        delete_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if delete_res.modified_count != 1:
            return 'Update error', False
        return 'Success', True
    except Exception as e:
        print(str(e))
        return str(e), False


def db_rename_favorite(username, new_name, favorite_id):
    try:
        print('enter db_rename_favorite')
        # pdb.set_trace()
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        fav['name'] = new_name

        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return 'OK',True
    except:
        return 'Key error', False

def db_select_all_favorites(username):
    try:
        item = db_select_user(username)
        return item['favorite'], True
    except Exception as e:
        return str(e), False

def db_verify_user(name, pw):
    try:
        find_res = db_select_user(name)
        if find_res is None:
            return False
        pw = 'NAME:' + name + '|PW:' + pw
        pwhash = find_res['pwhash']
        
        return check_password_hash(pwhash, pw)
    except:
        return False

def db_delete_user(name):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        delete_res = collection.delete_one(user)
        if delete_res.deleted_count != 1:
            return False
        return True
    except:
        return False

def db_update_user(name, newpw):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        newpwhash = generate_password_hash('NAME:'+name+'|PW:'+newpw, method='pbkdf2:sha256', salt_length=8)
        update_res = collection.update_one(user, {'$set':{'pwhash':newpwhash}})
        if update_res.modified_count != 1:
            return False
        return True
    except:
        return False

'''
{
    _id: <>
    title: 
    content:
    source:
    date:
}
'''

def db_list_info(page, perPage):
    try:
        collection = db["info"]
        find_res = collection.find(sort=[('_id', pymongo.DESCENDING)], skip=(page - 1) * perPage, limit=perPage)
        find_res = list(find_res)
        print(find_res)
        return find_res, True
    except Exception as e:
        print(e)
        return str(e), False

def db_list_problem(page, perPage):
    try:
        collection = db["question"]
        find_res = collection.find(sort=[('_id', pymongo.DESCENDING)], skip=(page - 1) * perPage, limit=perPage)
        find_res = list(find_res)
        print(find_res)
        return find_res, True
    except Exception as e:
        print(e)
        return str(e), False

def db_list_record(page=0, perPage=0):
    try:
        collection = db["record"]
        if page > 0:
            find_res = collection.find(sort=[('_id', pymongo.DESCENDING)], skip=(page - 1) * perPage, limit=perPage)
        else:
            find_res = collection.find(sort=[('_id', pymongo.DESCENDING)])
        find_res = list(find_res)
        print(find_res)
        return find_res, True
    except Exception as e:
        print(e)
        return str(e), False

def db_select_info(_id):
    try:
        collection = db["info"]
        info_data = {
            "_id": ObjectId(_id)
        }
        return collection.find_one(info_data)
    except Exception as e:
        return False

def db_next_info(_id=''):
    try:
        collection = db["info"]
        if _id == '':
            condition = None
        else:
            condition = {'_id':{'$lt':ObjectId(_id)}}
            # print(last_date)
        find_res = collection.find(filter=condition, sort=[('_id',pymongo.DESCENDING)], limit=5)
        find_res = list(find_res)
        return find_res
    except Exception as e:
        print(e)
        return False


def db_insert_info(title, content, source):
    try:
        collection = db["info"]
        info_data = {
            'title': title,
            'content': content,
            'source' : source,
            'date': datetime.datetime.now(),
        }
        collection.insert_one(info_data)
        return True
    except:
        return False

def db_delete_info(_id):
    try:
        collection = db["info"]
        info_data = {
            "_id": ObjectId(_id)
        }
        delete_res = collection.delete_one(info_data)
        if delete_res.deleted_count < 1:
            return False
        return True
    except Exception as e:
        print(e)
        return False

def db_update_info(_id, title, content, source):
    try:
        collection = db["info"]
        update_data = {
            'title': title,
            'content': content,
            'source' : source,
        }
        update_res = collection.update_one({'_id':ObjectId(_id)}, {"$set":update_data})
        if update_res.modified_count < 1:
            return False
        return True
    except Exception as e:
        print(e)
        return False
    

'''
questions
{
    _id: <>
    title     String   | 题目名                           |
    classification: int |单项选择题0/阅读程序题1/完善程序题2|
    submit_date: datetime.datetime.now()
    last_modified_date: datetime.datetime.now(),
    content:   string  | 题面
    code: string       | 代码块
    'subproblem': // 单选就一个元素且content留空，大题可能5-6个
    [{
        'content':'',//题干
        'choice':['']//2或4个
        },
    ],
    answer:    string[] 单选一个元素，多选多个元素,ABCD     |
    explanation: string[] 单选一个元素，多选多个元素        |
    source:    string  | 题目来源                         |
    owner:     string     | 创建者                        |
    nSubmit   Int      | 提交数                           |
    nAccept   Int      | ac数                             |
    correct_rate float  | 正确率,默认-1                   |
    tag       string[] | 标签                             |
    difficultyInt      | 难度,默认-1                      |
    hidden_mod   int  | 默认-1不隐藏/0隐藏                 |
}
'''

# search the library using id/source/owner/tag/difficultyInt
# _id='',title='',classification=[],source='',owner='',tag=[],difficultyInt=-1,last_modified_date='',nSubmit = -1,nAccept=-1,correct_rate =-1   
def db_select_questions(_id='',title='',classification=[],source='',owner='',
                        tag=[],difficultyInt=-1,submit_date='',last_modified_date='',
                        nSubmit = -1,nAccept=-1,correct_rate =-1):
    try:
        collection = db["question"]
        condition = {}
        if _id !='':
            condition['_id'] = ObjectId(_id)
        
        # 这里模糊查询可以修改
        if title != '':
            match_string = '/' + title + '/i'
            condition['title'] = {'$regex': match_string}
        if len(classification) != 0:
            condition['classification'] = classification    
        if source != '':
            condition['source'] = source
        if owner != '':
            condition['source'] = source
        # 这里的tag查询是部分匹配，只要满足一个tag即可
        if len(tag) != 0:
            condition['tag'] = tag    
        if difficultyInt != -1:
            condition['difficultyInt'] = difficultyInt
        if submit_date != '':
            condition['submit_date'] = {'$gte':submit_date} 
        if last_modified_date != '':
            condition['last_modified_date'] = {'$gte':last_modified_date}     
        if nSubmit != -1:
            condition['nSubmit'] = {'$gte':nSubmit}
        if nAccept != -1:
            condition['nAccept'] = {'$gte':nAccept}                 
        if correct_rate != -1:
            condition['correct_rate'] = {'$gte':correct_rate} 
            
        find_res = collection.find(filter=condition, sort=[('_id',pymongo.DESCENDING)])
        find_res = list(find_res)
        return find_res
    except Exception as e:
        return False

def db_insert_question(title='',classification=0,content='',code='', subproblem=[],
                        answer=[],explanation=[],source ='',owner='',
                        tag=[],difficultyInt=-1,hidden_mod=-1):
    try:
        collection = db["question"]
        question_data = {
            'title': title,
            'classification': classification,
            'submit_date': datetime.datetime.now(),
            'last_modified_date': datetime.datetime.now(),
            'content':content,
            'code':code,
            'subproblem':subproblem,
            'answer':answer,
            'explanation':explanation,
            'source':source,
            'owner':owner,
            'nSubmit':0,
            'nAccept':0,    
            # 'tag':tag,
            'difficultyInt':difficultyInt,
            # 'hidden_mod':hidden_mod, 
        }
        new_question_data = collection.insert_one(question_data)
        print('print insert result')
        questions_single_key = collection.find()
        print('list(questions_single_key) len is :',len(list(questions_single_key)))
        return True
    except Exception as e:
        print(e)
        return False

# _id 字段基本上是不可变的。在创建文档之后，根据定义，它已被分配了一个无法更改的 _id
def db_delete_question(_id):
    try:
        collection = db["question"]
        question_data = {
            "_id": ObjectId(_id)
        }
        delete_res = collection.delete_one(question_data)
        
        if delete_res.deleted_count < 1:
            return False
        return True
    except:
        return False

def db_update_question(_id='', title='',content='',code='',subproblem=[],
                        answer=[],explanation=[],source ='',owner='',
                        nSubmit=0,nAccept=0,correct_rate=-1,
                        tag=[],difficultyInt=-1,hidden_mod=-1):
    try:
        collection = db["question"]
        update_data = {
            'title': title,
            'last_modified_date': datetime.datetime.now(),
            'content':content,
            'code':code,
            'subproblem':subproblem,
            'answer':answer,
            'explanation':explanation,
            'source':source,
            'owner':owner,
            'nSubmit':nSubmit,
            'nAccept':nAccept,    
            'correct_rate':correct_rate,
            'tag':tag,
            'difficultyInt':difficultyInt,
            'hidden_mod':hidden_mod, 
        }
        print('begin update')
        # 如果没有set，会更换整个条目
        update_res = collection.update_one({'_id':ObjectId(_id)}, {"$set":update_data})
        print('finish update')
        if update_res.modified_count < 1:
            return False
        return True
    except:
        return False

'''
name_lists: 参加答题的所有用户名(还未确定)
required_amount_dic : 对应classification需要的题目数量
{
    '1':1,
    '2':3
}
difficulty_correct_rate_condition_dic: 根据难题模式/易错题模式
{
    '1':{
        'highest_difficulty':
        'lowest_difficulty':
        'highest_correct_rate':
        'lowest_correct_rate':
    }
    '2':3
}
'''

def db_get_random_questions(required_amount_dic={'0':3, '1':1}, difficulty_correct_rate_condition_dic={}):
    try:
        collection = db["question"] 
        questions = []
        condition = {}
        # TODO 把所有用户做过的题去除？
        pass

        for key,value in required_amount_dic.items():
            condition['classification'] = int(key)
            questions_single_key = collection.find(filter = condition)

            if difficulty_correct_rate_condition_dic: 
                print('difficulty_correct_rate_condition_dic',difficulty_correct_rate_condition_dic)
                difficulty_correct_rate_condition = difficulty_correct_rate_condition_dic[key]
                print('difficulty_correct_rate_condition',difficulty_correct_rate_condition)
                if 'highest_difficulty' in difficulty_correct_rate_condition:
                    condition['difficultyInt'].update({'$gte':difficulty_correct_rate_condition['highest_difficulty']})
                if 'lowest_difficulty' in difficulty_correct_rate_condition:
                    condition['difficultyInt'].update({'$lte':difficulty_correct_rate_condition['lowest_difficulty']}) 
                if 'highest_correct_rate' in difficulty_correct_rate_condition:
                    condition['correct_rate'].update({'$gte':difficulty_correct_rate_condition['highest_correct_rate']}) 
                if 'lowest_correct_rate' in difficulty_correct_rate_condition:
                    condition['correct_rate'].update({'$lte':difficulty_correct_rate_condition['lowest_correct_rate']})  
                # find_res = collection.find(filter=condition, sort=[('_id',pymongo.DESCENDING)])
                condition['$sample'] = {'size':value}
                print('end try')
                questions_single_key = collection.aggregate([condition])

            questions_single_key = list(questions_single_key)

            random_index = []
            if value <= len(questions_single_key):
                random_index = random.sample(range(0,len(questions_single_key)),value)
            else:
                random_index = random.sample(range(0,len(questions_single_key)),len(questions_single_key))
            print('random_index',random_index)

            result = []
            for i in random_index:
                result.append(questions_single_key[i].copy())

            print('after difficulty filter len(list(result)):',len(result))
            questions.extend(result.copy())

        print('len(questions)',len(questions))
        return questions
    except Exception as e:
        return False
