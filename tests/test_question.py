from flask import session
import json

# This file is pytest-related part, run "pytest" in terminal and automatically start a test

def test_insert(client):   
    return 
    question1_data = {
            'classification': 0,
            'content': '中国的国家顶级域名是：',
            'answer':['A'],
            'explanation':'china',
            'subproblem':[{'content':'', 'choice':['.cn','.hk','.us','.com']}],
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'hidden_mod':-1,   
        }
    question2_data = {
            'title': '常识',
            'classification': 0,
            'content': '中国的国家顶级域名是',
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
            'content': 
            '''void sort() // 排序
            for(int i=0; i<n; i++)
            for(int j=1; j<n; j++)
            if (①)
            {
                segment t = A[j];
                ②
            }
            1)①处应填()
            A. A[Jj].b > A[j - 1].b
            B.
            A[J].a < A[j - 1].a
            C. A[j].a > A[j - 1].a
            D. A[j].b < A[j - 1].b
            2)②处应填()
            A.A[j+1]=A[j];A[j]=t;
            B.A[j-1]=A[j];A[j]=t;
            C.A[j]=A[j+1];A[j+1]=t;
            D.A[j]=A[j-1];A[j-1]=t;
            ''',
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
        res = client.post('/question/insert-single/', json=question1_data)
        assert '200' in str(res)
        assert False
        res = client.post('/question/insert-single/', json=question2_data)
        assert '200' in str(res)
        res = client.post('/question/insert-single/', json=codequestion1_data)
        assert '200' in str(res)
        # res = client.post('/question/insert_big_single/', json=multi1_data)
        assert '200' in str(res)

        res = client.get('/question/random/')
        assert '200' in str(res)     
        res_second = json.loads(res.data)[0]
        res_second_id = res_second['id']
        question1_data['title'] = '计算机网络常识'
        question1_data['id'] = res_second_id
        res = client.post('/question/update-single/{}'.format(res_second_id), json=question1_data)
        assert '200' in str(res)      
        del question1_data['classification']
        res = client.post('/question/insert-single/', json=question1_data)
        assert '400' in str(res)
        res = client.get('/question/random-single/0')
        assert '200' in str(res)     
        res = client.get('/question/details/{}'.format(res_second_id))
        assert '200' in str(res)     
        res = client.delete('/question/delete/{}'.format(res_second_id))
        assert '200' in str(res)    
        res = client.delete('/question/delete-all/')
        assert '200' in str(res) 

def test_question_insert(client):
    question1_data = {
            'classification': 0,
            'content': '香港的顶级域名是：',
            'answer':['B'],
            'explanation':'us',
            'subproblem':[{'content':'', 'choice':['.cn','.hk','.us','.com']}],
            'source': 'CSP-J',
            'owner': 'panda',
            'nSubmit':0,
            'nAccept':0,    
            'correct_rate':0,
            'tag':['常识'],
            'difficultyInt':1,
            'hidden_mod':-1,
        } 
        
    with client:
        res = client.post('/question/insert-single/', json=question1_data)
        assert '200' in str(res)
        
