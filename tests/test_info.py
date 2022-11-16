from flask import session
import json

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_insert(client):
    
    info1_data = {
        "title": "Software Engineering",
        "source": "Article Generator",
        "content": '''Generally speaking, for me personally, software engineering is not just a momentous event, it can also change my life. In general, we all have to think carefully. How to implement software engineering. Knowing exactly what kind of existence software engineering is is the key to solving all problems. For me personally, software engineering is not just a momentous event, it can also change my life.
        '''
    }
    info2_data = {
        "title": "软件工程",
        "source": "文章生成器",
        "content": '''一般来说， 对我个人而言，软件工程不仅仅是一个重大的事件，还可能会改变我的人生。 一般来讲，我们都必须务必慎重的考虑考虑。 软件工程，到底应该如何实现。 了解清楚软件工程到底是一种怎么样的存在，是解决一切问题的关键。 对我个人而言，软件工程不仅仅是一个重大的事件，还可能会改变我的人生。
        '''
    }
    bad_info1_data = {
        "title": "Software Engineering",
        "source": "Article Generator",
    }
    
    with client:
         res = client.post('/info/insert/', json=info1_data)
         assert '200' in str(res)
         res = client.post('/info/insert/', json=bad_info1_data)
         assert "Bad Request",400 == res
         res = client.post('/info/insert/', json=info2_data)
         assert '200' in str(res)
         res = client.get('/info/get-latest/')
         res_first = json.loads(res.data)[0]
         res_first_id = res_first['id']
         assert '软件工程' in str(res_first)
         res = client.get('/info/get-latest/', json={'lastId':res_first_id})
         res_second = json.loads(res.data)[0]
         res_second_id = res_second['id']
         assert 'Software Engineering' in str(res_second)
         res = client.delete('/info/delete/{}'.format(res_first_id))
         assert '200' in str(res)
         res = client.get('/info/get-latest/', json={'lastId':''})
         assert 'Software Engineering' in str(json.loads(res.data)[0])
         res = client.get('/info/details/{}'.format(res_second_id))
         assert 'for me personally' in str(json.loads(res.data))
         res = client.delete('/info/delete/{}'.format(res_second_id))
         assert '200' in str(res)
         res = client.delete('/info/delete/{}'.format(res_second_id))
         assert '400' in str(res)
    
    question1_data = {
            'title': '常识',
            'classification': 0,
            'content': '中国的国家顶级域名是',
            'render_mod':-1,
            'answer':['A'],
            'explanation':'china',
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'pid':'1',
            'hidden_mod':-1,   
        }
    question2_data = {
            'title': '常识',
            'classification': 0,
            'content': '中国的国家顶级域名是',
            'render_mod':-1,
            'answer':['A'],
            'explanation':':)',
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'pid':'1',
            'hidden_mod':-1,   
        }
    multi1_question1_data = {
            'title': 'haha',
            'classification': 1,
            'content': 'fsdfdsfdsfsdfds',
            'render_mod':-1,
            'answer':['A'],
            'explanation':':)',
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'pid':'1',
            'hidden_mod':-1,   
        }
    multi1_question2_data = {
            'title': 'bbbb',
            'classification': 1,
            'content': 'fsdfdsfdsfsdfds',
            'render_mod':-1,
            'answer':['A'],
            'explanation':':)',
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'pid':'1',
            'hidden_mod':-1,   
        }
    codequestion1_data = {
            'title': 'code',
            'classification': 2,
            'content': 'void sort() // 排序\
            for(inti=0;i<n;i++)\
            for(intj=1;j<n;j++)\
if (①)\
{\
segment t = A[j];\
②\
}\
1)①处应填()\
A. A[Jj].b > A[j - 1].b\
B.\
A[J].a < A[j - 1].a\
C. A[j].a > A[j - 1].a\
D. A[j].b < A[j - 1].b\
2)②处应填()\
A.A[j+1]=A[j];A[j]=t;\
B.A[j-1]=A[j];A[j]=t;\
C.A[j]=A[j+1];A[j+1]=t;\
D.A[j]=A[j-1];A[j-1]=t;\
',
            'render_mod':-1,
            'answer':['A','A'],
            'explanation':':)',
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':2,
            'pid':'1',
            'hidden_mod':-1,   
        }
    multi1_data = {"data":[multi1_question1_data,multi1_question2_data]}

    with client:
        res = client.post('/question/insert_single/', json=question1_data)
        assert '200' in str(res)
        res = client.post('/question/insert_single/', json=question2_data)
        assert '200' in str(res)
        res = client.post('/question/insert_single/', json=codequestion1_data)
        assert '200' in str(res)
        res = client.post('/question/insert_big_single/', json=multi1_data)
        assert '200' in str(res)

        res = client.get('/question/random/')
        assert '200' in str(res)     
        res_second = json.loads(res.data)[0]
        res_second_id = res_second['id']
        question1_data['title'] = '计算机网络常识'
        question1_data['id'] = res_second_id
        res = client.post('/question/update_single/{}'.format(res_second_id), json=question1_data)
        assert '200' in str(res)      
        del question1_data['classification']
        res = client.post('/question/insert_single/', json=question1_data)
        assert '400' in str(res)
        res = client.get('/question/random_single/0')
        assert '200' in str(res)     
        res = client.get('/question/details/{}'.format(res_second_id))
        assert '200' in str(res)     
        res = client.delete('/question/delete/{}'.format(res_second_id))
        assert '200' in str(res)    
        res = client.delete('/question/delete_all/')
        assert '200' in str(res) 


def test_question_insert(client):
    pass
        
