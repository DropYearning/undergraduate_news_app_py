# news_app_py
毕业设计《基于Android的新闻推荐客户端设计与实现》新闻采集相关代码
- /log 目录存放日志文件，日志格式以“年份+月份+日期”命名
- newsUpdate.py 用与更新新闻数据库，适合在VPS用crontab定时执行
- newsCollect.py 用与初次采集新闻，每个频道采集2500条不到的历史新闻
- keysExtract.py 内有三种提取中文文本关键词的函数(From Jiebe and SnowNLP)
- 
