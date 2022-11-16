#backend


### 测试覆盖率
命令：
```
coverage run -m pytest && coverage report
```

请在backend/.coveragerc 中加入需要查看覆盖率的文件目录。目前是tests,views,sockets。

使用pytest的同时要看打印信息，请用命令
```
pytest -s
```
