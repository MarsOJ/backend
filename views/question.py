from bson.objectid import ObjectId
from views.database import *
from flask import Blueprint, Flask, request, session, jsonify
import pymongo
from bson.objectid import ObjectId
import datetime
import random

# 从前端接收答案后，判断答案是否正确的函数
# 前端返回一个string[]


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

def db_insert_single_question(title='',classification=-1,content='',render_mod=-1,
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

def db_insert_big_questions(data_list):
    try:
        collection = db["question"]
        first_question_id = ''
        print('enter db_insert_big_questions loop')
        print('data_list len is ',len(data_list))
        for i,data in enumerate(data_list):
            title = data['title']
            classification= data['classification']
            content= data['content']
            render_mod= data['render_mod']
            answer= data['answer']
            explanation= data['explanation']
            source= data['source']
            owner= data['owner']
            nSubmit= data['nSubmit']
            nAccept= data['nAccept'] 
            correct_rate= data['correct_rate']
            tag= data['tag']
            difficultyInt= data['difficultyInt']
            pid= data['pid']
            hidden_mod= data['hidden_mod']
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
                'hidden_mod':hidden_mod    
            }
            print('begin insert ',i)
            new_question_data = collection.insert_one(question_data)
            print('finish insert ',i)
        # TODO
            if i == 0:
                first_question_id = new_question_data.inserted_id
            collection.update_one({'_id':new_question_data.inserted_id}, {"$set":{'big_question_id':first_question_id}})
            print('finish update ',i)
        # print('hello')

        # print('print insert result')
        questions_single_key = collection.find()
        # print('list(questions_single_key) len is :',len(list(questions_single_key)))
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
        print('enter db_update_question')
        collection = db["question"]
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