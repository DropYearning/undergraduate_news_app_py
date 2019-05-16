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



def add_keywords_to_channel(channelName):
    # 记录开始时间
    starttime = datetime.datetime.now()
    sql_select = 'select * from %s ' % channelDict[channelName][1]
    # 使用 cursor()方法创建一个游标对象cursor
    cur = conn.cursor()
    cur.execute(sql_select)
    items = cur.fetchall()
    for item in items:
        keywords = keysExtract.keywords_by_jieba_TF(item[8])
        keywords_str = keywords[0] + "/" + keywords[1] + "/" + keywords[2]
        #print(keywords_str)
        # 在原表中插入插入关键词
        sql_update = "UPDATE %s set keywords='%s' WHERE id='%s' " % (channelDict[channelName][1], keywords_str, item[0])
        try:
            cur.execute(sql_update)
            # 提交到数据库执行
            conn.commit()
            print("INFO: 执行[%s]成功" % sql_update)
        except:
            print("INFO: 执行[%s]失败" % sql_update)
            conn.rollback()
    # 显示执行时间
    endtime = datetime.datetime.now()
    print("INFO: 本次花费时间[%s]s" % (endtime - starttime))


# 更新所有表
def add_keywords_to_Allchannel():

    # 记录开始时间
    start = datetime.datetime.now()
    for channel in channelDict:
        add_keywords_to_channel(channel)
    end = datetime.datetime.now()
    print("INFO: 一共花费时间[%s]s" % (end - start))


add_keywords_to_Allchannel()

# 释放连接
conn.close()

