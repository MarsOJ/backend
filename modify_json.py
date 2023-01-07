import json,copy

# Open file    
fileHandler  =  open("/home/ubuntu/backend_minan/problem.json",  "r")
# Get list of all lines in file
listOfLines  =  fileHandler.readlines()
# Close file
fileHandler.close()

new = []
# Iterate over the lines
for  line in  listOfLines:
    line = line.strip()
    json_data = json.loads(line)
    new_problem = {}

    if json_data["type"] == 0:
        new_problem['classification'] = 1
        new_problem['content'] = json_data["desc"]
        if 'code' in json_data:
            new_problem['code'] = json_data["code"]
        else:
            new_problem['code'] = ''
        new_problem['answer'] = [json_data['answer']]
        new_problem['explanation'] = json_data['sol']
        new_problem['source'] = json_data["tid"]

        if json_data["img"] != '':
            continue
        elif "imgsol" in json_data and json_data["imgsol"]!= '':
            continue
        else:
            a = [x['content'] for x in json_data["options"]]
            new_problem['subproblem'] = [{
                'content': '',
                'choice': [x['content'] for x in json_data["options"]]
            }]

            new.append(copy.deepcopy(new_problem))

with open('multichoice.json','w') as outf:
    for i in new:
        json.dump(i, outf, ensure_ascii=False)
        outf.write('\n')

'''
        classification= data['classification']
        content= data['content']
        answer= data['answer']
        explanation= data['explanation']
        subproblem = data['subproblem']
        source= data['source']
        owner= session['username']
        difficultyInt= data['difficultyInt']

        {
      'classification': 1,
      'content': '判断以下命题',
      'code':'```C++\n#include <cstdlib>\n...\n```'
      'answer':['B','C', 'A'],
      'explanation':'hk for .hk, us for .us, cn for .cn',
      'subproblem':[
          {'content':'香港的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
          {'content':'美国的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
          {'content':'中国的顶级域名是：', 'choice':['.cn','.hk','.us','.com']}, 
      ],
      'source': 'CSP-J',
      'difficultyInt':1,
  }


{"_id":"79550af260e5656124e96c081464b69e",
"_openid":"oGTqv5ROHbPgT-r944YOO-GytTXE",
"author":"oGTqv5ROHbPgT-r944YOO-GytTXE",
"code":"",
"img":"",
"options":[{"content":"bacde","option":"A"},{"content":"dbace","option":"B"},{"content":"dbcae","option":"C"},{"content":"ecbad","option":"D"}],
"score":5.0,
"sol":"简单模拟",
"tid":"C1004",
"type":0.0,
"answer":"C",
"class":"数据结构",
"desc":"某队列允许在其两端进行入队操作，但仅允许在一端进行出队操作。若元素abcde依次入此队列后再进行出队操作，则不可能得到的出队序列是"}

'''

# with open('/home/ubuntu/backend_minan/problem.json','r',encoding='utf8')as fp:
#     json_data = json.load(fp)
#     print('这是文件中的json数据：',json_data)
#     print('这是读取到文件数据的数据类型：', type(json_data))