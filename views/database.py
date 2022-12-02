from flask import Blueprint, Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from bson.objectid import ObjectId
import datetime
import random
import uuid

database_bp = Blueprint("database", __name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["MarsOJ"]

# use blueprint as app
@database_bp.route("/")
def database_index():
    return "Database Index"

def db_select_user(name):
    try:
        collection = db["account"]
        user = {
            'username':name
        }
        res = collection.find_one(user) # return dict
        return res
    except Exception as e:
        print(e)
        return False

def db_insert_user(name, pw):
    try:
        pwhash = generate_password_hash('NAME:'+name+'|PW:'+pw, method='pbkdf2:sha256', salt_length=8)
        collection = db["account"]
        user = {
            'username':name, 
            'pwhash':pwhash,
            'favorite':{'0':{'name':'default', 'problemID':[]}},
            'credit':0,
        }
        collection.insert_one(user)
        return True
    except:
        return False

def db_insert_favorite(username, favorite_name):
    try:
        item = db_select_user(username)

        favorites = item['favorite']
        names = [v['name'] for k,v in favorites]
        if favorite_name in names:
            return 'Repeated name', False
        favoriteID = uuid.uuid4()
        
        favorites[favoriteID]({
            'name':favorite_name,
            'problemID':[]
        })

        collection = db["account"]
        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return True
    except:
        return 'Key error', False

def db_insert_favorite_problem(username, favorite_id, problem_id):
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
            # check if problem in favorites
            if problem not in problem_set:
                noexist_num += 1
            # check if in dataset
            elif not db_select_questions(_id=problem):
                failed_num += 1
            else:
                problem_set.remove(problem)
                success_num += 1

        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            failed_num += success_num
            success_num = 0
        return (success_num, noexist_num, failed_num), True
    except:
        return 'Key error', False

def db_move_favorite_problem(username, problem_id, dest_id, source_id):
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
            if problem not in source_problem or problem in dest_problem:
                failed_num += 1
            else:
                dest_problem.append(problem)
                source_problem.remove(problem)
                success_num += 1

        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            failed_num += success_num
            success_num = 0
        return (success_num, failed_num), True
    except:
        return 'Key error', False

def db_delete_favorite_problem(username, favorite_id, problem_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        problem_set = fav['problemID']
        success_num = 0
        failed_num = 0
        repeated_num = 0
        add_items = []
        for problem in problem_id:
            # check if problem in favorites
            if problem in problem_set:
                repeated_num += 1
            # check if in dataset
            elif not db_select_questions(_id=problem):
                failed_num += 1
            else:
                add_items.append(problem)

        problem_set.extend(add_items)
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
        if delete_res.deleted_count != 1:
            return 'Update error', False
        return True
    except:
        return 'Key error', False

def db_rename_favorite(username, new_name, favorite_id):
    try:
        item = db_select_user(username)
        collection = db["account"]

        favorites = item['favorite']
        fav = favorites[favorite_id]
        fav['name'] = new_name

        update_res = collection.update_one({'username':username}, {'$set':{'favorite':favorites}})
        if update_res.modified_count != 1:
            return 'Update error', False
        return True
    except:
        return 'Key error', False

def db_select_all_favorites(username):
    try:
        item = db_select_user(username)
        return item['favorite']
    except Exception as e:
        return e, False

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
            last_date = db_select_info(_id)['date']
            condition = {'date':{'$lt':last_date}}
            print(last_date)
        find_res = collection.find(filter=condition, sort=[('date',pymongo.DESCENDING)], limit=5)
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
    except:
        return False

def db_update_info(_id, title, content, source):
    try:
        collection = db["info"]
        update_data = {
            'title': title,
            'content': content,
            'source' : source,
        }
        update_res = collection.update_one({'_id':ObjectId(_id)}, update_data)
        if update_res.modified_count < 1:
            return False
        return True
    except:
        return False
    

'''
questions
{
    _id: <>
    title     String   | 题目名                           |
    classification: int |单项选择题0/阅读程序题1/完善程序题2|
    submit_date: datetime.datetime.now()
    last_modified_date: datetime.datetime.now(),
    content:   string  | 题面                             |
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

def db_insert_question(title='',classification=0,content='',subproblem=[],
                        answer=[],explanation=[],source ='',owner='',
                        nSubmit=0,nAccept=0,correct_rate=-1,
                        tag=[],difficultyInt=-1,hidden_mod=-1):
    try:
        collection = db["question"]
        question_data = {
            'title': title,
            'classification': classification,
            'submit_date': datetime.datetime.now(),
            'last_modified_date': datetime.datetime.now(),
            'content':content,
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
        new_question_data = collection.insert_one(question_data)
        print('print insert result')
        questions_single_key = collection.find()
        print('list(questions_single_key) len is :',len(list(questions_single_key)))
        return True
    except Exception as e:
        print(e)
        return False

# _id 字段基本上是不可变的。在创建文档之后，根据定义，它已被分配了一个无法更改的 _id
# TODO
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

# def db_delete_database_all():
#     try:
#         print('enter db_delete_database_all')
#         collection = db["question"]
#         collection.drop()

#         return True
#     except:
#         return False


def db_update_question(_id='', title='',classification=0,content='',subproblem=[],
                        answer=[],explanation=[],source ='',owner='',
                        nSubmit=0,nAccept=0,correct_rate=-1,
                        tag=[],difficultyInt=-1,hidden_mod=-1):
    try:
        collection = db["question"]
        update_data = {
            'title': title,
            'classification': classification,
            'submit_date': datetime.datetime.now(),
            'last_modified_date': datetime.datetime.now(),
            'content':content,
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
