# coding:utf-8

import pymysql
import datetime
import jieba.analyse
import keysExtract

# 数据库连接参数
dbhost = "127.0.0.1"
dbport = 3306
dbuser = "root"
dbpasswd = "hdu123456"
dbname = "news_app"
dbcharset = "utf8"


# 新闻频道字典
channelDict = {
                '国内': ['5572a109b3cdc86cf39001db', 'news_domestic'],
                '国际': ['5572a109b3cdc86cf39001de', 'news_international'],
                '财经': ['5572a109b3cdc86cf39001e0', 'news_finance'],
                '互联网': ['5572a109b3cdc86cf39001e3', 'news_internet'],
                '房地产': ['5572a109b3cdc86cf39001e4', 'news_estate'], #数据源较差
                '汽车': ['5572a108b3cdc86cf39001d3', 'news_car'],
                '体育': ['5572a109b3cdc86cf39001e6', 'news_sport'],   #数据源较差
                '娱乐': ['5572a108b3cdc86cf39001d5', 'news_entertainment'],
                '游戏': ['5572a10ab3cdc86cf39001ee', 'news_game'],    #数据源较差
                '教育': ['5572a10ab3cdc86cf39001ef', 'news_edu'],     #数据源较差
                '科技': ['5572a10ab3cdc86cf39001f4', 'news_tech'],
                '军事': ['5572a109b3cdc86cf39001df', 'news_military'],
                '数码': ['5572a10bb3cdc86cf39001f5', 'news_digit'],
                '社会': ['5572a10bb3cdc86cf39001f8', 'news_society'],
               }


# 使用pymysql连接MySQL
conn = pymysql.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpasswd, db=dbname, charset=dbcharset)  # 创建数据库连接
cur = conn.cursor()  # 使用 cursor()方法创建一个游标对象cursor

cur.execute("UPDATE news_car set keywords='瓜子/二手车/用户' WHERE id='00b4f780c5a803286a2ce735ff454ffa' ")
# 提交到数据库执行
conn.commit()