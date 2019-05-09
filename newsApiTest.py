# coding:utf-8
import urllib.request
import json
import pymysql
from prettytable import PrettyTable
import hashlib
import datetime


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

# 请求相关参数(均以str存储)
para_channelId = "5572a108b3cdc86cf39001cd"        #请求的新闻频道ID
para_maxResult = "100"      #默认20,每页新闻数量,最大为100
para_needAllList = "0"     #是否需要返回所有的图片及段落属行allList。
para_needContent = "1"     #是否需要返回正文，1为需要，其他为不需要
para_needHtml = "1"        #是否需要返回正文的html格式，1为需要，其他为不需要
para_pageIndex = "1"          #当前请求的是列表的第几页

# 新闻频道字典
channelDict = {
                '国内': ['5572a108b3cdc86cf39001cd', 'demestic'],
                '国际': ['5572a108b3cdc86cf39001ce', 'international'],
                '军事': ['5572a108b3cdc86cf39001cf', 'military'],
                '财经': ['5572a108b3cdc86cf39001d0', 'finance'],
                '互联网': ['5572a108b3cdc86cf39001d1', 'internet'],
                '房地产': ['5572a108b3cdc86cf39001d2', 'estate'],
                '汽车': ['5572a108b3cdc86cf39001d3', 'car'],
                '体育': ['5572a108b3cdc86cf39001d4', 'sport'],
                '娱乐': ['5572a108b3cdc86cf39001d5', 'entertainment'],
                '游戏': ['5572a108b3cdc86cf39001d6', 'game'],
                '教育': ['5572a108b3cdc86cf39001d7', 'edu'],
                '科技': ['5572a108b3cdc86cf39001d9', 'tech']
               }

# 计算采集时间
starttime = datetime.datetime.now()

# 使用pymysql连接MySQL
conn = pymysql.connect(host=dbhost, port=dbport, user=dbuser, passwd=dbpasswd, db=dbname, charset=dbcharset)  # 创建数据库连接
cur = conn.cursor()  # 使用 cursor()方法创建一个游标对象cursor

# 参数拼接url
myQuerys = "channelId="+para_channelId+"&maxResult="+para_maxResult+"&needAllList="+para_needAllList+"&needContent="+para_needContent+"&needHtml="+para_needHtml+"&page="+para_pageIndex
bodys = {}
url = host + path + '?' + myQuerys

# 请求新闻列表
request = urllib.request.Request(url)
request.add_header('Authorization', 'APPCODE ' + appcode)
response = urllib.request.urlopen(request)
content = response.read()

# 解析json为dict格式
newsDict = json.loads(content)

# # 使用PrettyTable模块在终端格式化输出
# newsTable = PrettyTable(["newsId", "newsTitle", "newsLink", "newsChannelName", "newsSource", "newsPubtime",
#                          "newsHavePic","newsPicUrl1", "newsPicUrl2", "newsPicUrl3"])

# 新闻存储
newsCount = 0 # 计数

for item in newsDict['showapi_res_body']['pagebean']['contentlist']:
    newsChannelName = '国内焦点'
    newsSource = item['source']
    newsPubtime = item['pubDate']
    newsPicUrl1 = ""
    newsPicUrl2 = ""
    newsPicUrl3 = ""
    # 获取当前时间作为新闻入库时间戳
    newsSaveTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    # newsTable.add_row([newsMD5, newsTitle, newsLink, newsChannelName, newsSource, newsPubtime, picNum, newsPicUrl1, newsPicUrl2, newsPicUrl3])

    # 新闻入库
    cur.execute("SELECT id FROM news_finance WHERE id=%s", newsMD5)
    checkExist = cur.fetchone()
    if checkExist != None:# 新闻去重
        print("[%s]" % newsSaveTime, "WANR: 新闻[%s]已存在!" % newsTitle )
    else:
        newsCount = newsCount + 1
        # 定义SQL插入语句
        SQL_INSERT = "INSERT INTO news_finance(id, title, channelName, source, pubtime, savetime, link, havepic, content , html, picurl1, picurl2, picurl3) VALUES ('%s', \"%s\", '%s', '%s', '%s', '%s', '%s', %d, \"%s\", \"%s\",'%s', '%s', '%s')" % (newsMD5, newsTitle, newsChannelName, newsSource, newsPubtime, newsSaveTime, newsLink, picNum, newsContent,newsHTML, newsPicUrl1, newsPicUrl2, newsPicUrl3)
        cur.execute(SQL_INSERT)
        # 提交到数据库执行
        conn.commit()

# print(newsTable)
# 日志输出
print("[%s]" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO: 本次入库新闻数量[%s]条" % newsCount )
# 显示采集时间
endtime = datetime.datetime.now()
print("[%s]" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO: 本次采集花费时间[%s]s" % (endtime - starttime))
# 释放连接
conn.close()

