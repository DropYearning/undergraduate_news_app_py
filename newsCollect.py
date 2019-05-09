# newsCollect.py
# 用在初次采集新闻数据, 采集约2500*12条新闻数据
# 由于通过新闻API采集到的新闻并不严格按照发布时间pubtime排序
# 因此初次采集时将newspubtime作为newsSaveTime入库

# coding:utf-8
import  urllib.request
import json
import pymysql
from prettytable import PrettyTable
import hashlib
import datetime
import os.path
import time


# 新闻API相关参数（from:全国热门带正文新闻查询_易源数据【阿里云】）
host = 'http://ali-news.showapi.com'
path = '/newsList'
method = 'GET'
appcode = '54d1f6bc0a9f455498f4e83553cab3a1'

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

firstCollectStart = datetime.datetime.now()

# 函数channelCollect用于对某个频道进行首次数据采集
def channelCollect(channel):
    """
    :param url: API请求url
    :param channel: 请求的新闻频道字典key
    :return: 无
    """
    # 计算单个频道首次采集时间
    starttime = datetime.datetime.now()
    # 新闻计数
    newsCount = 0

    # 请求相关参数(均以str存储)
    para_channelId = channelDict[channel][0]  # 请求的新闻频道ID
    para_channelName = channel
    para_maxResult = "50"  # 默认20,每页新闻数量,最大为100
    para_needAllList = "0"  # 是否需要返回所有的图片及段落属行allList。
    para_needContent = "1"  # 是否需要返回正文，1为需要，其他为不需要
    para_needHtml = "1"  # 是否需要返回正文的html格式，1为需要，其他为不需要
    tableName = channelDict[channel][1]

    # 每个频道采集50*50 = 2500 不到的新闻
    for k in range(1, 50):
        # print(k)
        para_pageIndex = str(k)  # 当前请求的是列表的第几页
        # 参数拼接url
        myQuerys = "channelId=" + para_channelId + "&maxResult=" + para_maxResult + "&needAllList=" + para_needAllList + "&needContent=" + para_needContent + "&needHtml=" + para_needHtml + "&page=" + para_pageIndex
        bodys = {}
        url = host + path + '?' + myQuerys

        # 请求新闻列表
        request = urllib.request.Request(url)
        request.add_header('Authorization', 'APPCODE ' + appcode)
        response = urllib.request.urlopen(request)
        content = response.read()
        # 解析json为dict格式
        newsDict = json.loads(content)

        # 遍历分析每篇新闻
        for item in newsDict['showapi_res_body']['pagebean']['contentlist']:
            newsChannelName = para_channelName
            newsSource = item['source']
            newsPubtime = item['pubDate']
            newsPicUrl1 = ""
            newsPicUrl2 = ""
            newsPicUrl3 = ""
            # 用MD5算法处理新闻Url作为数据库主键ID
            newsLink = item['link']
            m = hashlib.md5()
            m.update(newsLink.encode(encoding='utf-8'))
            newsMD5 = m.hexdigest()
            # 标题\正文\HTML文件中可能存在影响数据库写入的引号,使用pymysql的pymysql.escape_string(html)方法对内容中的引号自动转义
            rowTitle = item['title']
            rowContent = item['content']
            rowHTML = item['html']
            newsTitle = pymysql.escape_string(rowTitle)
            newsContent = pymysql.escape_string(rowContent)
            newsHTML = pymysql.escape_string(rowHTML)
            picNum = len(item['imageurls'])
            # 处理图片信息
            try:
                if item['havePic']:
                    if picNum == 1:
                        newsPicUrl1 = item['imageurls'][0]['url']
                    elif picNum == 2:
                        newsPicUrl1 = item['imageurls'][0]['url']
                        newsPicUrl2 = item['imageurls'][1]['url']
                    elif picNum == 3:
                        newsPicUrl1 = item['imageurls'][0]['url']
                        newsPicUrl2 = item['imageurls'][1]['url']
                        newsPicUrl3 = item['imageurls'][2]['url']
                    else:
                        picNum = 3
                        newsPicUrl1 = item['imageurls'][0]['url']
                        newsPicUrl2 = item['imageurls'][1]['url']
                        newsPicUrl3 = item['imageurls'][2]['url']
            except KeyError:
                picNum = 0
            # 新闻入库
            SQL_CHECK = "SELECT id FROM %s WHERE id=\"%s\"" % (tableName, newsMD5)
            cur.execute(SQL_CHECK)
            checkExist = cur.fetchone()
            # 获取当前时间作为新闻入库时间戳
            newsSaveTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if checkExist != None:# 新闻去重
                print("[%s]" % newsSaveTime, "WANR: [%s]类新闻[%s]已存在!" % (para_channelName,newsTitle))
            else:
                if len(newsContent) == 0:
                    print("[%s]" % newsSaveTime, "WANR: [%s]类新闻[%s]正文为空!" % (para_channelName,newsTitle))
                else:

                    newsCount = newsCount + 1
                    # 定义SQL插入语句
                    SQL_INSERT = "INSERT INTO %s (id, title, channelName, source, pubtime, savetime, link, havepic, content , html, picurl1, picurl2, picurl3) VALUES ('%s', \"%s\", '%s', '%s', '%s', '%s', '%s', %d, \"%s\", \"%s\",'%s', '%s', '%s')" % (tableName, newsMD5, newsTitle, newsChannelName, newsSource, newsPubtime, newsPubtime, newsLink, picNum, newsContent,newsHTML, newsPicUrl1, newsPicUrl2, newsPicUrl3)
                    try:
                        # print("新闻[%s]已保存" % newsTitle)
                        cur.execute(SQL_INSERT)
                        # 提交到数据库执行
                        conn.commit()
                    except:
                        conn.rollback()
                        newsCount = newsCount - 1


    # 日志输出
    print("[%s]" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO: 本次收录[%s]新闻[%s]条" % (channel, newsCount))
    # 显示采集时间
    endtime = datetime.datetime.now()
    print("[%s]" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          "INFO: 本次采集花费时间[%s]s" % (endtime - starttime))
    # 等待30s,防止短时间内大量请求
    # time.sleep(30)

# 对每个频道进行初次采集
for key in channelDict:
    channelCollect(key)

firstCollectEnd = datetime.datetime.now()
print("[%s]" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO: 首次采集共花费时间[%s]s" % (firstCollectEnd - firstCollectStart))

# 释放连接
conn.close()
