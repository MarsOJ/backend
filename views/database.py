from flask import Blueprint, Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from bson.objectid import ObjectId
import datetime
import random

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
        return collection.find_one(user) # return dict
    except Exception as e:
        print(e)
        return False

def db_insert_user(name, pw):
    try:
        pwhash = generate_password_hash('NAME:'+name+'|PW:'+pw, method='pbkdf2:sha256', salt_length=8)
        collection = db["account"]
        user = {
            'username':name, 
            'pwhash':pwhash
        }
        collection.insert_one(user)
        return True
    except:
        return False

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
    classification: int |无多小问单选0/多个小问单选1/无多小问代码单选2/多个小问代码单选3/判断4/非代码填空3/代码填空4/多选5|
    submit_date: datetime.datetime.now()
    last_modified_date: datetime.datetime.now(),
    content:   string  | 题面                             |
    render_mod:  int   |默认-1/无0/markdown1/html2                |
    answer:    string[] 不同类型的题目对应答案格式不同
    explanation: string[] |
    source:    string  | 题目来源
    owner:     string     | 创建者                           |
    nSubmit   Int      | 提交数                           |
    nAccept   Int      | ac数                             |
    correct_rate float  | 正确率,默认-1                   |
    tag       string[] | 标签                             |
    difficultyInt      | 难度,默认-1                      |
    
    pid       string   |题号（用户自定义）               |
    hidden_mod   int  | 默认-1不隐藏/0隐藏                 |  
    big_question_id:<> | 每个题都默认有多个小问,默认一个大题的big_question_id是第一小问的id|
    
    # 暂时没加入的                
    domainId  string   | 所属域                           |
    docType   Int32    | 10                               |
    docId     Int32    | 题目id(auto increment, unique)   |
    data      obejct[] | 数据点信息                       |
    config    String   | 配置信息                         |
    stats     Object   | 提交信息                         |

}
'''

# search the library using id/source/owner/tag/difficultyInt
# _id='',title='',classification=[],source='',owner='',tag=[],difficultyInt=-1,last_modified_date='',nSubmit = -1,nAccept=-1,correct_rate =-1   
def db_select_questions(_id='',title='',classification=[],source='',owner='',
                        tag=[],difficultyInt=-1,submit_date='',last_modified_date='',
                        nSubmit = -1,nAccept=-1,correct_rate =-1):
    try:
        collection = db["quesion"]
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

def db_insert_question(title='',classification=-1,content='',render_mod=-1,
                        answer=[],explanation=[],source ='',owner='',
                        nSubmit=0,nAccept=0,correct_rate=-1,
                        tag=[],difficultyInt=-1,
                        pid='',hidden_mod=-1,
                        big_question_id=''):
    try:
        collection = db["question"]
        question_data = {
            'title': title,
            'classification': classification,
            'submit_date': datetime.datetime.now(),
            'last_modified_date': datetime.datetime.now(),
            'content':content,
            'render_mod':render_mod,
            'answer':answer,
            'explanation':explanation,
            'source':source,
            'owner':owner,
            'nSubmit':nSubmit,
            'nAccept':nAccept,    
            'correct_rate':correct_rate,
            'tag':tag,
            'difficultyInt':difficultyInt,
            'pid':pid,
            'hidden_mod':hidden_mod,
            'big_question_id':big_question_id     
        }
        new_question_data = collection.insert_one(question_data)
        # TODO
        if big_question_id=='':
            collection.update_one({'_id':new_question_data.inserted_id}, {"$set":{'big_question_id':new_question_data.inserted_id}})
        # print('hello')

        print('print insert result')
        questions_single_key = collection.find()
        print('list(questions_single_key) len is :',len(list(questions_single_key)))
        return True
    except:
        return False

# _id 字段基本上是不可变的。在创建文档之后，根据定义，它已被分配了一个无法更改的 _id
# TODO
def db_delete_question(_id,big_question_id=''):
    try:
        collection = db["question"]
        question_data = {
            "_id": ObjectId(_id)
        }
        delete_res = collection.delete_one(question_data)
        
        if big_question_id != '':
            question_big_data = {
            "big_question_id": ObjectId(big_question_id)
            }
            delete_res_big = collection.delete_one(question_big_data)
        if delete_res.deleted_count < 1 and delete_res_big.deleted_count < 1:
            return False
        return True
    except:
        return False

def db_delete_question_all():
    try:
        print('enter db_delete_question_all')
        collection = db["question"]
        collection.drop()

        return True
    except:
        return False


def db_update_question(_id, title='',classification=-1,last_modified_date='',content='',render_mod=-1,
                        answer=[],explanation=[],source ='',owner='',
                        nSubmit=0,nAccept=0,correct_rate=-1,
                        tag=[],difficultyInt=-1,
                        pid='',hidden_mod=-1,
                        big_question_id=''):
    try:
        collection = db["info"]
        update_data = {
            'title': title,
            'classification': classification,
            'last_modified_date': datetime.datetime.now(),
            'content':content,
            'render_mod':render_mod,
            'answer':answer,
            'explanation':explanation,
            'source':source,
            'owner':owner,
            'nSubmit':nSubmit,
            'nAccept':nAccept,    
            'correct_rate':correct_rate,
            'tag':tag,
            'difficultyInt':difficultyInt,
            'pid':pid,
            'hidden_mod':hidden_mod,
            'big_question_id':big_question_id     
        }
        update_res = collection.update_one({'_id':ObjectId(_id)}, update_data)
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

def db_get_random_questions(names_list=[],required_amount_dic={},difficulty_correct_rate_condition_dic={}):
    try:
        # if len(names_list) == 0:
        #     return False,"the length of the name list is zero"
        collection = db["question"] 
        # print('print db_get_random_questions start result')
        # questions_single_key = collection.find()
        # print('list(questions_single_key) len is :',len(list(questions_single_key)))
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
            else:
                pass


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